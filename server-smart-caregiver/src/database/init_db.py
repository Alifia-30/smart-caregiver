"""
Database initialization utilities.

Usage (one-time setup or in tests):
    asyncio.run(create_tables())

For production, use Alembic migrations instead of create_tables().
"""

import asyncio

from src.database.base import Base
from src.database.session import engine

# Must import all models so they are registered with Base.metadata
import src.database.models  # noqa: F401


async def create_tables() -> None:
    """Create all tables. Safe for dev/testing; use Alembic for production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully.")


async def drop_tables() -> None:
    """Drop all tables. DANGER: irreversible in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("All tables dropped.")


if __name__ == "__main__":
    asyncio.run(create_tables())
