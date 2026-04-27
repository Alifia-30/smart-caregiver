from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app.core.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
# Neon requires sslmode=require. asyncpg uses ssl=True instead of a query param.
# pool_pre_ping=True handles Neon's serverless cold-start connection drops.
engine = create_async_engine(
    settings.DATABASE_URL,                 # postgresql+asyncpg://user:pass@host/db
    echo=settings.DB_ECHO,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require",                  # Neon enforces TLS
        "server_settings": {
            "application_name": "caregiver_app",
        },
    },
)

# ── Session factory ───────────────────────────────────────────────────────────
# expire_on_commit=False prevents lazy-load errors after commit in async context
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ── FastAPI dependency ────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
