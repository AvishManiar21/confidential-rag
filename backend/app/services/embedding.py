"""Embedding service using sentence-transformers."""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        """Initialize the embedding model."""
        self.model_name = settings.embedding_model
        self._model = None
        logger.info(f"Initializing embedding service with model: {self.model_name}")

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        return self._model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List[float]: Embedding vector
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar

        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            int: Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()

    async def compute_similarity(
        self,
        embedding1: Union[List[float], np.ndarray],
        embedding2: Union[List[float], np.ndarray]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            float: Cosine similarity score (0-1)
        """
        try:
            emb1 = np.array(embedding1) if isinstance(embedding1, list) else embedding1
            emb2 = np.array(embedding2) if isinstance(embedding2, list) else embedding2

            # Cosine similarity
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise

    async def compute_batch_similarity(
        self,
        query_embedding: Union[List[float], np.ndarray],
        document_embeddings: List[Union[List[float], np.ndarray]]
    ) -> List[float]:
        """
        Compute cosine similarity between a query and multiple documents.

        Args:
            query_embedding: Query embedding vector
            document_embeddings: List of document embedding vectors

        Returns:
            List[float]: List of similarity scores
        """
        try:
            query_emb = np.array(query_embedding) if isinstance(query_embedding, list) else query_embedding
            doc_embs = np.array([
                np.array(emb) if isinstance(emb, list) else emb
                for emb in document_embeddings
            ])

            # Compute cosine similarity for all documents at once
            similarities = np.dot(doc_embs, query_emb) / (
                np.linalg.norm(doc_embs, axis=1) * np.linalg.norm(query_emb)
            )
            return similarities.tolist()
        except Exception as e:
            logger.error(f"Error computing batch similarity: {str(e)}")
            raise


# Global instance
embedding_service = EmbeddingService()
