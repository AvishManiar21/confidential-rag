"""RAG service for hybrid retrieval and answer generation."""

from typing import List, Dict, Any, Optional, Tuple
import time
from rank_bm25 import BM25Okapi
import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.embedding import embedding_service
from app.services.chroma import chroma_service
from app.services.commitment import commitment_service

settings = get_settings()
logger = get_logger(__name__)


class RAGService:
    """Service for RAG query processing with hybrid retrieval."""

    def __init__(self):
        """Initialize RAG service."""
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model
        self.top_k = settings.top_k_retrieval
        self.similarity_threshold = settings.similarity_threshold
        logger.info("Initialized RAG service")

    async def hybrid_retrieve(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval combining BM25 and vector search.

        Args:
            query: Query text
            top_k: Number of results to return
            alpha: Weight for vector search (0=BM25 only, 1=vector only)
            metadata_filter: Optional metadata filter for ChromaDB

        Returns:
            List[Dict]: Retrieved documents with scores
        """
        try:
            start_time = time.time()

            # Generate query embedding
            query_embedding = await embedding_service.embed_text(query)

            # Vector search using ChromaDB
            vector_results = await chroma_service.query_by_embedding(
                query_embedding=query_embedding,
                n_results=top_k * 2,  # Get more for fusion
                where=metadata_filter
            )

            # Extract documents for BM25
            documents = vector_results['documents'][0]
            doc_ids = vector_results['ids'][0]
            metadatas = vector_results['metadatas'][0]
            distances = vector_results['distances'][0]

            if not documents:
                logger.warning("No documents retrieved from ChromaDB")
                return []

            # Convert distances to similarity scores (cosine similarity)
            vector_scores = [1 - (dist / 2) for dist in distances]

            # BM25 scoring
            tokenized_docs = [doc.lower().split() for doc in documents]
            tokenized_query = query.lower().split()

            bm25 = BM25Okapi(tokenized_docs)
            bm25_scores = bm25.get_scores(tokenized_query)

            # Normalize scores to 0-1 range
            max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
            bm25_scores_norm = [score / max_bm25 for score in bm25_scores]

            # Hybrid scoring with alpha weighting
            hybrid_scores = [
                alpha * vec_score + (1 - alpha) * bm25_score
                for vec_score, bm25_score in zip(vector_scores, bm25_scores_norm)
            ]

            # Combine results
            results = []
            for i, (doc_id, doc, metadata, hybrid_score, vec_score, bm25_score) in enumerate(
                zip(doc_ids, documents, metadatas, hybrid_scores, vector_scores, bm25_scores_norm)
            ):
                results.append({
                    "id": doc_id,
                    "content": doc,
                    "metadata": metadata,
                    "hybrid_score": hybrid_score,
                    "vector_score": vec_score,
                    "bm25_score": bm25_score
                })

            # Sort by hybrid score and take top_k
            results.sort(key=lambda x: x["hybrid_score"], reverse=True)
            results = results[:top_k]

            # Filter by similarity threshold
            results = [r for r in results if r["vector_score"] >= self.similarity_threshold]

            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Hybrid retrieval completed in {elapsed:.2f}ms, retrieved {len(results)} documents")

            return results

        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {str(e)}")
            raise

    async def generate_answer(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        max_context_length: int = 2000
    ) -> str:
        """
        Generate answer using Ollama LLM.

        Args:
            query: User query
            context_docs: Retrieved context documents
            max_context_length: Maximum context length

        Returns:
            str: Generated answer
        """
        try:
            # Build context from retrieved documents
            context_parts = []
            total_length = 0

            for doc in context_docs:
                content = doc["content"]
                if total_length + len(content) > max_context_length:
                    # Truncate if too long
                    remaining = max_context_length - total_length
                    content = content[:remaining]

                context_parts.append(content)
                total_length += len(content)

                if total_length >= max_context_length:
                    break

            context = "\n\n".join(context_parts)

            # Create prompt
            prompt = f"""Based on the following context, answer the question. If the answer cannot be found in the context, say so.

Context:
{context}

Question: {query}

Answer:"""

            # Call Ollama API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                answer = result.get("response", "")

            logger.info(f"Generated answer ({len(answer)} chars)")
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    async def query(
        self,
        query_text: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        generate_answer: bool = True
    ) -> Dict[str, Any]:
        """
        Process RAG query with hybrid retrieval.

        Args:
            query_text: Query text
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity threshold
            metadata_filter: Optional metadata filter
            generate_answer: Whether to generate an answer

        Returns:
            Dict: Query results with retrieved docs and answer
        """
        try:
            start_time = time.time()

            # Use defaults if not provided
            top_k = top_k or self.top_k
            similarity_threshold = similarity_threshold or self.similarity_threshold

            # Hybrid retrieval
            retrieved_docs = await self.hybrid_retrieve(
                query=query_text,
                top_k=top_k,
                metadata_filter=metadata_filter
            )

            # Generate answer if requested
            answer = ""
            if generate_answer and retrieved_docs:
                answer = await self.generate_answer(
                    query=query_text,
                    context_docs=retrieved_docs
                )

            # Calculate metrics
            avg_similarity = (
                sum(doc["vector_score"] for doc in retrieved_docs) / len(retrieved_docs)
                if retrieved_docs else 0.0
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            result = {
                "query": query_text,
                "retrieved_documents": retrieved_docs,
                "answer": answer,
                "num_results": len(retrieved_docs),
                "avg_similarity": avg_similarity,
                "response_time_ms": response_time_ms
            }

            logger.info(
                f"RAG query completed in {response_time_ms}ms: "
                f"{len(retrieved_docs)} docs, avg_sim={avg_similarity:.3f}"
            )

            return result

        except Exception as e:
            logger.error(f"Error processing RAG query: {str(e)}")
            raise

    async def evaluate_with_ragas(
        self,
        query: str,
        answer: str,
        context_docs: List[Dict[str, Any]],
        ground_truth: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate RAG response using RAGAS metrics.

        Args:
            query: Query text
            answer: Generated answer
            context_docs: Retrieved context documents
            ground_truth: Optional ground truth answer

        Returns:
            Dict: RAGAS metrics
        """
        try:
            # Placeholder for RAGAS evaluation
            # In production, this would use the RAGAS library

            logger.info("Evaluating with RAGAS metrics")

            # Mock metrics
            metrics = {
                "faithfulness": 0.85,
                "answer_relevancy": 0.80,
                "context_precision": 0.75,
                "context_recall": 0.78,
                "overall_score": 0.80
            }

            # TODO: Implement actual RAGAS evaluation
            # from ragas import evaluate
            # from ragas.metrics import faithfulness, answer_relevancy

            return metrics

        except Exception as e:
            logger.error(f"Error evaluating with RAGAS: {str(e)}")
            return {}


# Global instance
rag_service = RAGService()
