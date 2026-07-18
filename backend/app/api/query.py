"""RAG query endpoint with ZK proof generation."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import time

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.query import QueryAudit
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    RetrievedDocument,
    ZKProof,
    ErrorResponse
)
from app.services.rag import rag_service
from app.services.commitment import commitment_service
from app.services.merkle import merkle_service
from app.services.midnight import midnight_service

router = APIRouter()
logger = get_logger(__name__)


async def generate_zk_proof(
    query_hash: str,
    retrieved_docs: list,
    response_hash: str
) -> Optional[ZKProof]:
    """
    Generate zero-knowledge proof for query response.

    Args:
        query_hash: Hash of the query
        retrieved_docs: Retrieved documents
        response_hash: Hash of the response

    Returns:
        ZKProof: Generated proof or None
    """
    try:
        start_time = time.time()

        # Collect document commitments
        commitments = [doc["metadata"].get("commitment") for doc in retrieved_docs]
        commitments = [c for c in commitments if c]  # Filter None values

        if not commitments:
            logger.warning("No commitments found in retrieved documents")
            return None

        # Build Merkle tree from commitments
        merkle_tree = await merkle_service.build_tree(commitments)
        merkle_root = merkle_tree.get_root()

        # Generate Merkle proof for first document
        merkle_proof = await merkle_service.generate_proof(
            merkle_tree, commitments[0]
        )

        # Create proof data
        proof_data = {
            "query_hash": query_hash,
            "response_hash": response_hash,
            "merkle_root": merkle_root,
            "merkle_proof": merkle_proof,
            "num_documents": len(commitments),
            "commitments": commitments
        }

        # Verify proof on Midnight (optional)
        verified = False
        try:
            verification_result = await midnight_service.verify_proof(
                proof_data=proof_data,
                merkle_root=merkle_root
            )
            verified = verification_result.get("verified", False)
        except Exception as e:
            logger.warning(f"Proof verification failed: {str(e)}")

        verification_time_ms = int((time.time() - start_time) * 1000)

        return ZKProof(
            proof_type="merkle_proof",
            proof_data=proof_data,
            verified=verified,
            verification_time_ms=verification_time_ms
        )

    except Exception as e:
        logger.error(f"Error generating ZK proof: {str(e)}")
        return None


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process RAG query with ZK proof generation.

    Steps:
    1. Hybrid retrieval (BM25 + vector search)
    2. Generate answer using Ollama
    3. Generate ZK proof
    4. Log query to audit table
    5. Return response with proof
    """
    try:
        start_time = time.time()

        # Generate query hash
        query_hash = commitment_service.hash_query(
            request.query,
            metadata={"user_id": request.user_id, "session_id": request.session_id}
        )

        # Create audit record
        audit = QueryAudit(
            query_text=request.query,
            query_hash=query_hash,
            user_id=request.user_id,
            session_id=request.session_id,
            status="processing"
        )
        db.add(audit)
        await db.flush()

        try:
            # Perform RAG query
            rag_result = await rag_service.query(
                query_text=request.query,
                top_k=request.top_k,
                similarity_threshold=request.similarity_threshold,
                metadata_filter=request.metadata_filter,
                generate_answer=True
            )

            retrieved_docs = rag_result["retrieved_documents"]
            answer = rag_result["answer"]
            avg_similarity = rag_result["avg_similarity"]

            # Update audit record
            audit.num_results = len(retrieved_docs)
            audit.retrieved_docs = [
                {
                    "id": doc["id"],
                    "score": doc["hybrid_score"],
                    "metadata": doc["metadata"]
                }
                for doc in retrieved_docs
            ]
            audit.relevance_scores = [doc["hybrid_score"] for doc in retrieved_docs]
            audit.response_text = answer
            audit.avg_similarity = avg_similarity

            # Generate response hash
            response_hash = commitment_service.hash_text(answer)
            audit.response_hash = response_hash

            # Generate ZK proof if requested
            proof = None
            if request.generate_proof and retrieved_docs:
                proof = await generate_zk_proof(
                    query_hash=query_hash,
                    retrieved_docs=retrieved_docs,
                    response_hash=response_hash
                )

                if proof:
                    audit.proof_generated = True
                    audit.proof_verified = proof.verified
                    audit.proof_data = proof.proof_data

            # Evaluate with RAGAS (optional)
            ragas_score = None
            try:
                ragas_metrics = await rag_service.evaluate_with_ragas(
                    query=request.query,
                    answer=answer,
                    context_docs=retrieved_docs
                )
                ragas_score = ragas_metrics.get("overall_score")
                audit.ragas_score = ragas_score
            except Exception as e:
                logger.warning(f"RAGAS evaluation failed: {str(e)}")

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            audit.response_time_ms = response_time_ms
            audit.status = "completed"
            audit.completed_at = datetime.utcnow()

            await db.commit()
            await db.refresh(audit)

            # Build response
            return QueryResponse(
                query=request.query,
                response=answer,
                retrieved_documents=[
                    RetrievedDocument(
                        document_id=int(doc["metadata"].get("document_id", 0)),
                        chunk_id=doc["id"],
                        content=doc["content"],
                        score=doc["hybrid_score"],
                        metadata=doc["metadata"]
                    )
                    for doc in retrieved_docs
                ],
                ragas_score=ragas_score,
                avg_similarity=avg_similarity,
                proof=proof,
                response_time_ms=response_time_ms,
                query_id=audit.id
            )

        except Exception as e:
            # Update audit with error
            audit.status = "failed"
            audit.error_message = str(e)
            audit.completed_at = datetime.utcnow()
            await db.commit()
            raise

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query/{query_id}")
async def get_query_audit(
    query_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get query audit record by ID."""
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(QueryAudit).where(QueryAudit.id == query_id)
        )
        audit = result.scalar_one_or_none()

        if not audit:
            raise HTTPException(status_code=404, detail="Query not found")

        return audit.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting query audit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
