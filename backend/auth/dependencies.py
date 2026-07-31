"""
CyberShield XDR — Auth Dependencies
FastAPI dependency injection for authentication and authorization.

Usage in endpoints:
    @router.get("/protected")
    async def endpoint(user: CurrentUser):  # requires any authenticated user
        ...

    @router.delete("/admin-only")
    async def admin_endpoint(user: AdminUser):  # requires admin role
        ...
"""
from typing import Annotated
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.security import decode_token
from backend.config.logging_config import get_logger
from backend.database.redis_client import RedisKeys, get_redis
from backend.database.session import get_db
from backend.models.user import User, UserRole

logger = get_logger(__name__)

# Extracts Bearer token from Authorization header
bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
) -> User:
    """
    Core auth dependency — validates JWT and returns the User ORM object.

    Checks:
    1. Token signature and expiry (jose)
    2. Token type is "access" (prevents refresh token reuse)
    3. JTI not in blacklist (handles logout)
    4. User exists and is active in DB
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except JWTError as exc:
        logger.warning(f"JWT decode failed: {exc}")
        raise credentials_exception

    user_id: str = payload.get("sub")
    jti: str = payload.get("jti", "")

    if not user_id:
        raise credentials_exception

    # Check token blacklist (covers logout and rotation)
    if await redis.exists(RedisKeys.blacklist(jti)):
        logger.warning(f"Blacklisted token used by user {user_id}")
        raise credentials_exception

    # Load user from DB
    result = await db.execute(
        select(User).where(User.id == UUID(user_id), User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    return user


# ---------------------------------------------------------------------------
# Role-based access control dependencies
# ---------------------------------------------------------------------------

def require_roles(*roles: UserRole):
    """
    Factory that returns a dependency enforcing one of the given roles.

    Usage:
        @router.post("/scan", dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.SOC_ANALYST))])
    """
    async def _check(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in roles]}",
            )
        return user
    return _check


# ---------------------------------------------------------------------------
# Convenience type aliases for common role combinations
# ---------------------------------------------------------------------------

# Any authenticated user
CurrentUser = Annotated[User, Depends(get_current_user)]

# Admin only
AdminUser = Annotated[
    User,
    Depends(require_roles(UserRole.ADMIN)),
]

# Admin or SOC Analyst
AnalystUser = Annotated[
    User,
    Depends(require_roles(UserRole.ADMIN, UserRole.SOC_ANALYST)),
]
