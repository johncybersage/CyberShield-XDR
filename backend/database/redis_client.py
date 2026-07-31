"""
CyberShield XDR — Redis Client
Async Redis connection pool used for:
- Refresh token storage (hashed)
- Token blacklist (logout / rotation)
- Rate limiting counters
- Login attempt counters
"""
from typing import Optional

import redis.asyncio as aioredis

from backend.config.logging_config import get_logger
from backend.config.settings import get_settings

settings = get_settings()
logger = get_logger(__name__)

# Module-level pool — created once, shared across requests
_redis_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """
    FastAPI dependency that returns the shared Redis connection.
    Pool is created on first call and reused.
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        logger.info("Redis connection pool created")
    return _redis_pool


async def close_redis() -> None:
    """Close Redis pool on application shutdown."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("Redis connection pool closed")


# ---------------------------------------------------------------------------
# Typed Redis operations used by auth
# ---------------------------------------------------------------------------

class RedisKeys:
    """Centralised key templates — prevents typos and key collisions."""

    @staticmethod
    def refresh_token(token_hash: str) -> str:
        return f"cybershield:refresh:{token_hash}"

    @staticmethod
    def blacklist(jti: str) -> str:
        return f"cybershield:blacklist:{jti}"

    @staticmethod
    def login_attempts(identifier: str) -> str:
        return f"cybershield:login_attempts:{identifier}"

    @staticmethod
    def rate_limit(identifier: str, endpoint: str) -> str:
        return f"cybershield:rate:{endpoint}:{identifier}"

    @staticmethod
    def lockout(user_id: str) -> str:
        return f"cybershield:lockout:{user_id}"
