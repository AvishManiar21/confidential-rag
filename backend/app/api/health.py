"""Health check endpoint."""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import HealthResponse
from app.services.chroma import chroma_service
from app.services.midnight import midnight_service
from app import __version__

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.

    Returns system status and service availability.
    """
    services = {
        "database": "unknown",
        "chromadb": "unknown",
        "midnight": "unknown",
        "ollama": "unknown"
    }

    # Check database
    try:
        await db.execute("SELECT 1")
        services["database"] = "healthy"
    except Exception:
        services["database"] = "unhealthy"

    # Check ChromaDB
    try:
        count = await chroma_service.count_documents()
        services["chromadb"] = f"healthy ({count} docs)"
    except Exception:
        services["chromadb"] = "unhealthy"

    # Check Midnight
    try:
        is_connected = await midnight_service.check_connection()
        services["midnight"] = "healthy" if is_connected else "unhealthy"
    except Exception:
        services["midnight"] = "unhealthy"

    # Determine overall status
    status = "healthy" if all(
        s.startswith("healthy") for s in services.values()
    ) else "degraded"

    return HealthResponse(
        status=status,
        version=__version__,
        timestamp=datetime.utcnow(),
        services=services
    )
