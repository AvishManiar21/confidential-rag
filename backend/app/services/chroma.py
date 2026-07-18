"""ChromaDB service for vector storage and retrieval."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class ChromaDBService:
    """Service for interacting with ChromaDB vector database."""

    def __init__(self):
        """Initialize ChromaDB client."""
        self._client = None
        self._collection = None
        self.collection_name = "confidential_rag"
        logger.info("Initializing ChromaDB service")

    @property
    def client(self) -> chromadb.Client:
        """Lazy load ChromaDB client."""
        if self._client is None:
            try:
                # Use HTTP client for remote ChromaDB
                self._client = chromadb.HttpClient(
                    host=settings.chroma_url.replace("http://", "").split(":")[0],
                    port=int(settings.chroma_url.split(":")[-1]) if ":" in settings.chroma_url else 8000,
                )
                logger.info(f"Connected to ChromaDB at {settings.chroma_url}")
            except Exception as e:
                logger.error(f"Failed to connect to ChromaDB: {str(e)}")
                logger.info("Falling back to in-memory ChromaDB")
                self._client = chromadb.Client()
        return self._client

    @property
    def collection(self) -> chromadb.Collection:
        """Get or create the document collection."""
        if self._collection is None:
            try:
                self._collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "ConfidentialRAG document embeddings"}
                )
                logger.info(f"Using collection: {self.collection_name}")
            except Exception as e:
                logger.error(f"Error accessing collection: {str(e)}")
                raise
        return self._collection

    async def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """
        Add documents with embeddings to ChromaDB.

        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs

        Returns:
            bool: Success status
        """
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise

    async def query_by_embedding(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query documents by embedding vector.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions

        Returns:
            Dict containing ids, documents, metadatas, distances
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=["documents", "metadatas", "distances"]
            )
            logger.info(f"Retrieved {len(results['ids'][0])} results from ChromaDB")
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise

    async def query_by_text(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query documents by text (ChromaDB will embed automatically).

        Args:
            query_texts: List of query texts
            n_results: Number of results to return
            where: Metadata filter conditions

        Returns:
            Dict containing ids, documents, metadatas, distances
        """
        try:
            results = self.collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB by text: {str(e)}")
            raise

    async def get_by_ids(self, ids: List[str]) -> Dict[str, Any]:
        """
        Get documents by their IDs.

        Args:
            ids: List of document IDs

        Returns:
            Dict containing documents and metadatas
        """
        try:
            results = self.collection.get(
                ids=ids,
                include=["documents", "metadatas", "embeddings"]
            )
            return results
        except Exception as e:
            logger.error(f"Error getting documents by IDs: {str(e)}")
            raise

    async def delete_by_ids(self, ids: List[str]) -> bool:
        """
        Delete documents by their IDs.

        Args:
            ids: List of document IDs to delete

        Returns:
            bool: Success status
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise

    async def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Update existing documents.

        Args:
            ids: List of document IDs to update
            documents: Optional new document texts
            embeddings: Optional new embeddings
            metadatas: Optional new metadata

        Returns:
            bool: Success status
        """
        try:
            self.collection.update(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"Updated {len(ids)} documents in ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error updating documents: {str(e)}")
            raise

    async def count_documents(self) -> int:
        """
        Get total count of documents in collection.

        Returns:
            int: Number of documents
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting documents: {str(e)}")
            return 0

    async def reset_collection(self) -> bool:
        """
        Delete all documents from the collection.

        Returns:
            bool: Success status
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self._collection = None
            logger.warning(f"Reset collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            raise


# Global instance
chroma_service = ChromaDBService()
