"""
CyberShield XDR — Database Engine & Session Factory
Async SQLAlchemy with connection pooling optimized for production load.
Engine is created lazily on first use to avoid import-time driver errors.
"""
import asyncio
from typing import AsyncGenerator, Optional

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.config.logging_config import get_logger
from backend.config.settings import get_settings

logger = get_logger(__name__)

# Naming convention for Alembic auto-migrations
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# ---------------------------------------------------------------------------
# Lazy engine — created on first access, not at import time.
# This prevents asyncpg import errors when running tests or CLI tools
# that don't need a real DB connection.
# ---------------------------------------------------------------------------

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


def get_engine() -> AsyncEngine:
    """Return the shared async engine, creating it on first call."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.is_development,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"server_settings": {"application_name": settings.app_name}},
        )
    return _engine


def get_session_factory() -> async_sessionmaker:
    """Return the shared session factory, creating it on first call."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


# Convenience alias used by Alembic env.py and workers
@property
def engine() -> AsyncEngine:
    return get_engine()


# Keep AsyncSessionLocal as a callable for backwards compatibility
class _LazySessionLocal:
    """Proxy that creates the session factory on first call."""
    def __call__(self):
        return get_session_factory()()

    def __enter__(self):
        return get_session_factory().__enter__()

    def __exit__(self, *args):
        return get_session_factory().__exit__(*args)


AsyncSessionLocal = _LazySessionLocal()


_db_semaphore: Optional[asyncio.Semaphore] = None

def get_db_semaphore() -> asyncio.Semaphore:
    """Return a shared semaphore to throttle concurrent database connections."""
    global _db_semaphore
    if _db_semaphore is None:
        # Match the connection pool size (pool_size 10 + max_overflow 20)
        _db_semaphore = asyncio.Semaphore(30)
    return _db_semaphore


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session per request.
    Uses a semaphore to prevent Connection Pool exhaustion under high load.
    Automatically commits on success, rolls back on exception.
    """
    async with get_db_semaphore():
        async with get_session_factory()() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


async def init_db() -> None:
    """Create all tables. Used in development; production uses Alembic migrations."""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")


async def close_db() -> None:
    """Dispose engine connection pool on application shutdown."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
    logger.info("Database connection pool closed")
