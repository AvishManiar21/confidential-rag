"""FastAPI application for ConfidentialRAG backend."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.core.logging import setup_logging, get_logger
from app.api import health, documents, query
from app import __version__

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.project_name} v{__version__}")
    logger.info(f"Debug mode: {settings.debug}")

    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")

    yield

    # Shutdown
    logger.info("Shutting down application")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="Confidential RAG with Zero-Knowledge Proofs and Midnight Blockchain",
    version=__version__,
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


# Include routers
app.include_router(
    health.router,
    prefix=settings.api_v1_prefix,
    tags=["health"]
)

app.include_router(
    documents.router,
    prefix=settings.api_v1_prefix,
    tags=["documents"]
)

app.include_router(
    query.router,
    prefix=settings.api_v1_prefix,
    tags=["query"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.project_name}",
        "version": __version__,
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health"
    }


@app.get("/info")
async def info():
    """Application information."""
    return {
        "name": settings.project_name,
        "version": __version__,
        "debug": settings.debug,
        "api_version": "v1",
        "features": [
            "Document ingestion with PDF support",
            "Hybrid retrieval (BM25 + vector search)",
            "RAG with Ollama LLM",
            "Zero-knowledge proof generation",
            "Merkle tree commitments",
            "Midnight blockchain integration",
            "RAGAS evaluation metrics"
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
