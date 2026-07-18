"""Document management endpoints."""

from datetime import datetime
from typing import Optional
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import pypdf
import hashlib

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.document import Document
from app.models.schemas import (
    DocumentResponse,
    DocumentList,
    UploadResponse,
    ErrorResponse
)
from app.services.embedding import embedding_service
from app.services.chroma import chroma_service
from app.services.commitment import commitment_service
from app.services.merkle import merkle_service, MerkleTree
from app.services.midnight import midnight_service
from app.core.config import get_settings

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


async def process_pdf(file_content: bytes) -> tuple[str, list[str]]:
    """
    Extract text from PDF and split into chunks.

    Args:
        file_content: PDF file bytes

    Returns:
        tuple: (full_text, chunks)
    """
    try:
        # Read PDF
        pdf_file = io.BytesIO(file_content)
        pdf_reader = pypdf.PdfReader(pdf_file)

        # Extract text from all pages
        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        full_text = "\n\n".join(text_parts)

        # Simple chunking by character count with overlap
        chunks = []
        chunk_size = settings.chunk_size
        chunk_overlap = settings.chunk_overlap

        start = 0
        while start < len(full_text):
            end = start + chunk_size
            chunk = full_text[start:end]
            chunks.append(chunk.strip())
            start += chunk_size - chunk_overlap

        return full_text, chunks

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise


@router.post("/documents", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and process a document.

    Steps:
    1. Read file and compute hash
    2. Extract text and create chunks
    3. Generate embeddings
    4. Store in ChromaDB
    5. Generate commitments and Merkle tree
    6. Submit to Midnight contract
    7. Save metadata to PostgreSQL
    """
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Compute file hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Check if already exists
        result = await db.execute(
            select(Document).where(Document.file_hash == file_hash)
        )
        existing_doc = result.scalar_one_or_none()

        if existing_doc:
            raise HTTPException(
                status_code=400,
                detail=f"Document already exists with ID: {existing_doc.id}"
            )

        # Create document record
        doc = Document(
            filename=file.filename,
            file_hash=file_hash,
            file_size=file_size,
            content_type=file.content_type or "application/pdf",
            processed=False
        )
        db.add(doc)
        await db.flush()

        # Process PDF
        try:
            full_text, chunks = await process_pdf(file_content)
            doc.text_content = full_text
            doc.num_chunks = len(chunks)

            # Generate embeddings
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = await embedding_service.embed_batch(chunks, show_progress=True)

            # Generate embedding hashes
            embedding_hashes = commitment_service.hash_embedding_batch(embeddings)
            doc.embedding_hash = hashlib.sha256(
                "".join(embedding_hashes).encode('utf-8')
            ).hexdigest()

            # Generate chunk commitments
            chunk_hashes = [
                commitment_service.hash_text(chunk) for chunk in chunks
            ]
            commitments = await commitment_service.generate_batch_commitments(
                document_hashes=chunk_hashes,
                embedding_hashes=embedding_hashes
            )

            # Build Merkle tree
            merkle_tree = await merkle_service.build_tree(commitments)
            merkle_root = merkle_tree.get_root()
            doc.merkle_root = merkle_root

            # Generate document commitment
            doc.commitment = await commitment_service.generate_commitment(
                document_hash=file_hash,
                embedding_hash=doc.embedding_hash
            )

            # Store in ChromaDB
            logger.info("Storing embeddings in ChromaDB")
            chunk_ids = [f"{doc.id}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "document_id": doc.id,
                    "chunk_index": i,
                    "filename": file.filename,
                    "commitment": commitments[i]
                }
                for i in range(len(chunks))
            ]

            await chroma_service.add_documents(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids
            )

            # Generate Merkle proof for first chunk (example)
            merkle_proof = await merkle_service.generate_proof(
                merkle_tree, commitments[0]
            )
            doc.merkle_proof = merkle_proof

            # Submit to Midnight contract
            try:
                logger.info("Submitting commitment to Midnight")
                tx_result = await midnight_service.submit_commitment(
                    commitment_hash=doc.commitment,
                    merkle_root=merkle_root,
                    metadata={"document_id": doc.id, "filename": file.filename}
                )
                doc.tx_hash = tx_result.get("tx_hash")
                doc.block_number = tx_result.get("block_number")
            except Exception as e:
                logger.warning(f"Failed to submit to Midnight: {str(e)}")

            # Mark as processed
            doc.processed = True
            doc.processed_at = datetime.utcnow()
            await db.commit()
            await db.refresh(doc)

            logger.info(f"Document {doc.id} processed successfully")

            return UploadResponse(
                message="Document uploaded and processed successfully",
                document=DocumentResponse.model_validate(doc),
                processing_started=True
            )

        except Exception as e:
            doc.error_message = str(e)
            await db.commit()
            raise

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentList)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    processed_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    List all documents with pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        processed_only: Only return processed documents
    """
    try:
        # Build query
        query = select(Document)
        if processed_only:
            query = query.where(Document.processed == True)

        query = query.order_by(Document.created_at.desc())

        # Get total count
        count_query = select(func.count()).select_from(Document)
        if processed_only:
            count_query = count_query.where(Document.processed == True)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        documents = result.scalars().all()

        return DocumentList(
            total=total,
            documents=[DocumentResponse.model_validate(doc) for doc in documents],
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document by ID."""
    try:
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        doc = result.scalar_one_or_none()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentResponse.model_validate(doc)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and its embeddings."""
    try:
        # Get document
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        doc = result.scalar_one_or_none()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete from ChromaDB
        try:
            chunk_ids = [f"{doc.id}_{i}" for i in range(doc.num_chunks)]
            await chroma_service.delete_by_ids(chunk_ids)
        except Exception as e:
            logger.warning(f"Error deleting from ChromaDB: {str(e)}")

        # Delete from database
        await db.delete(doc)
        await db.commit()

        logger.info(f"Document {document_id} deleted")

        return {"message": "Document deleted successfully", "document_id": document_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
