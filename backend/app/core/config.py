"""Application configuration."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    database_url: str  # Required - must be set via environment variable

    # ChromaDB
    chroma_url: str = "http://localhost:8000"
    chroma_auth_token: str  # Required - must be set via environment variable

    # Ollama
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # Midnight
    midnight_node_url: str = "http://localhost:8080"
    midnight_indexer_url: str = "http://localhost:8081"
    midnight_proof_server_url: str = "http://localhost:6300"
    midnight_contract_address: Optional[str] = None
    midnight_private_key: Optional[str] = None

    # RAG Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_retrieval: int = 5

    # RAGAS Configuration
    ragas_threshold: float = 0.7
    similarity_threshold: float = 0.6

    # Application
    debug: bool = True
    log_level: str = "INFO"

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "ConfidentialRAG"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Security
    secret_key: str = "CHANGE_ME"
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
