"""
CyberShield XDR — Pytest Configuration
Async test setup with isolated test database and Redis mock.
"""
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database.redis_client import get_redis
from backend.database.session import Base, get_db
from backend.main import create_app

# Use SQLite for tests (no PostgreSQL required in CI)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Isolated DB session per test — rolled back after each test."""
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def redis_mock():
    """In-memory Redis mock using fakeredis."""
    try:
        import fakeredis.aioredis as fakeredis
        r = fakeredis.FakeRedis()
        yield r
        await r.aclose()
    except ImportError:
        pytest.skip("fakeredis not installed")


@pytest_asyncio.fixture
async def client(db_session, redis_mock) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client with dependency overrides."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_redis] = lambda: redis_mock

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
