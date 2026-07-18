#!/usr/bin/env python
"""Setup database tables."""

import asyncio
from app.core.database import init_db
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def main():
    """Initialize database tables."""
    try:
        logger.info("Creating database tables...")
        await init_db()
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
