"""Commitment service for generating cryptographic commitments and hashes."""

from typing import List, Dict, Any
import hashlib
import json
from eth_hash.auto import keccak

from app.core.logging import get_logger

logger = get_logger(__name__)


class CommitmentService:
    """Service for generating cryptographic commitments for ZK proofs."""

    @staticmethod
    def hash_text(text: str) -> str:
        """
        Generate SHA-256 hash of text.

        Args:
            text: Input text

        Returns:
            str: Hex-encoded hash
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """
        Generate SHA-256 hash of bytes.

        Args:
            data: Input bytes

        Returns:
            str: Hex-encoded hash
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def keccak_hash(data: str) -> str:
        """
        Generate Keccak-256 hash (Ethereum-compatible).

        Args:
            data: Input data as string

        Returns:
            str: Hex-encoded Keccak hash
        """
        return keccak(data.encode('utf-8')).hex()

    @staticmethod
    def hash_embedding(embedding: List[float]) -> str:
        """
        Generate hash of an embedding vector.

        Args:
            embedding: Embedding vector

        Returns:
            str: Hex-encoded hash
        """
        # Convert embedding to bytes representation
        embedding_str = json.dumps(embedding, sort_keys=True)
        return hashlib.sha256(embedding_str.encode('utf-8')).hexdigest()

    @staticmethod
    def hash_embedding_batch(embeddings: List[List[float]]) -> List[str]:
        """
        Generate hashes for multiple embeddings.

        Args:
            embeddings: List of embedding vectors

        Returns:
            List[str]: List of hex-encoded hashes
        """
        return [CommitmentService.hash_embedding(emb) for emb in embeddings]

    @staticmethod
    async def generate_commitment(
        document_hash: str,
        embedding_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a commitment for a document.

        Commitment = Hash(document_hash || embedding_hash || metadata)

        Args:
            document_hash: Hash of the document content
            embedding_hash: Hash of the embedding vector
            metadata: Optional metadata to include in commitment

        Returns:
            str: Hex-encoded commitment hash
        """
        try:
            # Combine hashes
            combined = document_hash + embedding_hash

            # Add metadata if provided
            if metadata:
                metadata_str = json.dumps(metadata, sort_keys=True)
                combined += metadata_str

            # Generate final commitment
            commitment = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            logger.debug(f"Generated commitment: {commitment}")
            return commitment

        except Exception as e:
            logger.error(f"Error generating commitment: {str(e)}")
            raise

    @staticmethod
    async def generate_batch_commitments(
        document_hashes: List[str],
        embedding_hashes: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Generate commitments for multiple documents.

        Args:
            document_hashes: List of document hashes
            embedding_hashes: List of embedding hashes
            metadatas: Optional list of metadata dicts

        Returns:
            List[str]: List of commitment hashes
        """
        try:
            commitments = []
            metadatas = metadatas or [None] * len(document_hashes)

            for doc_hash, emb_hash, metadata in zip(document_hashes, embedding_hashes, metadatas):
                commitment = await CommitmentService.generate_commitment(
                    doc_hash, emb_hash, metadata
                )
                commitments.append(commitment)

            logger.info(f"Generated {len(commitments)} commitments")
            return commitments

        except Exception as e:
            logger.error(f"Error generating batch commitments: {str(e)}")
            raise

    @staticmethod
    async def verify_commitment(
        commitment: str,
        document_hash: str,
        embedding_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Verify a commitment matches the provided data.

        Args:
            commitment: Commitment to verify
            document_hash: Document hash
            embedding_hash: Embedding hash
            metadata: Optional metadata

        Returns:
            bool: True if commitment is valid
        """
        try:
            # Regenerate commitment
            regenerated = await CommitmentService.generate_commitment(
                document_hash, embedding_hash, metadata
            )

            # Compare
            is_valid = commitment == regenerated
            logger.debug(f"Commitment verification: {is_valid}")
            return is_valid

        except Exception as e:
            logger.error(f"Error verifying commitment: {str(e)}")
            return False

    @staticmethod
    def hash_query(query_text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate hash for a query.

        Args:
            query_text: Query text
            metadata: Optional metadata

        Returns:
            str: Hex-encoded query hash
        """
        combined = query_text
        if metadata:
            combined += json.dumps(metadata, sort_keys=True)

        return hashlib.sha256(combined.encode('utf-8')).hexdigest()


# Global instance
commitment_service = CommitmentService()
