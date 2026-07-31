"""
CyberShield XDR — Authentication Service
All auth business logic lives here, keeping endpoints thin.

Security features implemented:
- Account lockout after N failed attempts (Redis-backed, auto-expires)
- Refresh token rotation (old token blacklisted on each refresh)
- Password reset via time-limited signed JWT (no DB state needed)
- Audit log entry for every auth event
- Automatic bcrypt rehash if rounds config changes
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    needs_rehash,
    verify_password,
)
from backend.config.logging_config import get_logger
from backend.config.settings import get_settings
from backend.database.redis_client import RedisKeys
from backend.models.audit_log import AuditLog
from backend.models.user import User, UserRole
from backend.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)

settings = get_settings()
logger = get_logger(__name__)

# Refresh token TTL in seconds
REFRESH_TTL = settings.jwt_refresh_token_expire_days * 86400
ACCESS_EXPIRE_SECONDS = settings.jwt_access_token_expire_minutes * 60


class AuthService:
    """
    Stateless service — all state lives in PostgreSQL and Redis.
    Instantiated per-request via FastAPI dependency injection.
    """

    def __init__(self, db: AsyncSession, redis: aioredis.Redis):
        self.db = db
        self.redis = redis

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    async def register(self, data: RegisterRequest, request: Optional[Request] = None) -> TokenResponse:
        """
        Register a new user.
        - Checks email and username uniqueness
        - Hashes password before storage
        - Issues tokens immediately (no email verification required for MVP)
        """
        # Uniqueness checks
        existing = await self.db.execute(
            select(User).where(
                (User.email == data.email) | (User.username == data.username)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email or username already registered",
            )

        user = User(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=UserRole.VIEWER,  # Default role — admin promotes manually
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.flush()  # Get the generated UUID

        await self._audit(
            user=user,
            action="user.register",
            status="success",
            request=request,
        )

        logger.info(f"New user registered: {user.email} [{user.id}]")
        return await self._issue_tokens(user)

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    async def login(self, data: LoginRequest, request: Optional[Request] = None) -> TokenResponse:
        """
        Authenticate user with email + password.
        Implements account lockout: after MAX_LOGIN_ATTEMPTS failures,
        the account is locked for LOCKOUT_DURATION_MINUTES.
        """
        # Load user
        result = await self.db.execute(
            select(User).where(User.email == data.email, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()

        # Generic error — don't reveal whether email exists
        auth_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

        if user is None:
            # Still check lockout key to prevent timing oracle on email enumeration
            await self._increment_attempts(data.email)
            raise auth_error

        # Check lockout
        await self._check_lockout(str(user.id), data.email)

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled. Contact your administrator.",
            )

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            await self._record_failed_attempt(user, request)
            raise auth_error

        # Successful login — clear failure counters
        await self._clear_attempts(str(user.id), user.email)

        # Rehash if bcrypt rounds config changed
        if needs_rehash(user.hashed_password):
            user.hashed_password = hash_password(data.password)

        await self._audit(user=user, action="user.login", status="success", request=request)
        logger.info(f"User logged in: {user.email}")
        return await self._issue_tokens(user)

    # ------------------------------------------------------------------
    # Token Refresh
    # ------------------------------------------------------------------

    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        """
        Issue new access + refresh tokens using a valid refresh token.
        Old refresh token is blacklisted immediately (rotation).
        """
        try:
            payload = decode_token(data.refresh_token, expected_type="refresh")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload["sub"]
        jti = payload.get("jti", "")
        token_hash = hash_refresh_token(data.refresh_token)

        # Verify token exists in Redis (proves it was issued by us and not revoked)
        stored = await self.redis.get(RedisKeys.refresh_token(token_hash))
        if not stored or stored != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or already used",
            )

        # Load user
        result = await self.db.execute(
            select(User).where(User.id == UUID(user_id), User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        # Rotate: delete old token, blacklist its JTI
        await self.redis.delete(RedisKeys.refresh_token(token_hash))
        await self.redis.setex(RedisKeys.blacklist(jti), REFRESH_TTL, "1")

        logger.debug(f"Token refreshed for user {user.email}")
        return await self._issue_tokens(user)

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    async def logout(
        self,
        user: User,
        access_token: str,
        refresh_token: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> None:
        """
        Invalidate the current session.
        - Blacklists the access token JTI
        - Deletes the refresh token from Redis
        """
        try:
            payload = decode_token(access_token, expected_type="access")
            jti = payload.get("jti", "")
            exp = payload.get("exp", 0)
            ttl = max(int(exp - datetime.now(timezone.utc).timestamp()), 1)
            await self.redis.setex(RedisKeys.blacklist(jti), ttl, "1")
        except JWTError:
            pass  # Token already invalid — logout is idempotent

        if refresh_token:
            token_hash = hash_refresh_token(refresh_token)
            await self.redis.delete(RedisKeys.refresh_token(token_hash))

        await self._audit(user=user, action="user.logout", status="success", request=request)
        logger.info(f"User logged out: {user.email}")

    # ------------------------------------------------------------------
    # Password Reset
    # ------------------------------------------------------------------

    async def forgot_password(self, email: str) -> Optional[str]:
        """
        Generate a password reset token.
        Returns the token (caller sends it via email).
        Always returns success message to prevent email enumeration.
        """
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            return None  # Caller returns generic success regardless

        token = create_reset_token(str(user.id))
        # Store token hash in Redis with 15-minute TTL
        token_hash = hash_refresh_token(token)
        await self.redis.setex(
            f"cybershield:reset:{token_hash}",
            900,  # 15 minutes
            str(user.id),
        )
        logger.info(f"Password reset token generated for {email}")
        return token

    async def reset_password(self, data: ResetPasswordRequest) -> None:
        """
        Reset password using a valid reset token.
        Token is single-use — deleted from Redis after use.
        """
        try:
            payload = decode_token(data.token, expected_type="reset")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        user_id = payload["sub"]
        token_hash = hash_refresh_token(data.token)
        redis_key = f"cybershield:reset:{token_hash}"

        stored = await self.redis.get(redis_key)
        if not stored or stored != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token already used or expired",
            )

        result = await self.db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.hashed_password = hash_password(data.new_password)
        await self.redis.delete(redis_key)  # Single-use

        # Invalidate all existing refresh tokens for this user
        await self._revoke_all_user_tokens(str(user.id))

        await self._audit(user=user, action="user.password_reset", status="success")
        logger.info(f"Password reset completed for {user.email}")

    async def change_password(
        self, user: User, data: ChangePasswordRequest, request: Optional[Request] = None
    ) -> None:
        """Change password for an authenticated user (requires current password)."""
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        user.hashed_password = hash_password(data.new_password)
        await self._revoke_all_user_tokens(str(user.id))
        await self._audit(user=user, action="user.password_change", status="success", request=request)
        logger.info(f"Password changed for {user.email}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _issue_tokens(self, user: User) -> TokenResponse:
        """Create access + refresh token pair and store refresh token in Redis."""
        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role.value,
            email=user.email,
        )
        refresh_token = create_refresh_token(user_id=str(user.id))

        # Store hashed refresh token in Redis
        token_hash = hash_refresh_token(refresh_token)
        await self.redis.setex(
            RedisKeys.refresh_token(token_hash),
            REFRESH_TTL,
            str(user.id),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_EXPIRE_SECONDS,
            user=UserResponse.model_validate(user),
        )

    async def _check_lockout(self, user_id: str, email: str) -> None:
        """Raise 429 if the account is currently locked out."""
        lockout_key = RedisKeys.lockout(user_id)
        if await self.redis.exists(lockout_key):
            ttl = await self.redis.ttl(lockout_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked. Try again in {ttl // 60 + 1} minutes.",
                headers={"Retry-After": str(ttl)},
            )

    async def _increment_attempts(self, identifier: str) -> None:
        """Increment failed attempt counter (used for unknown emails)."""
        key = RedisKeys.login_attempts(identifier)
        await self.redis.incr(key)
        await self.redis.expire(key, settings.lockout_duration_minutes * 60)

    async def _record_failed_attempt(self, user: User, request: Optional[Request]) -> None:
        """Increment failed attempts for a known user; lock if threshold reached."""
        key = RedisKeys.login_attempts(str(user.id))
        attempts = await self.redis.incr(key)
        await self.redis.expire(key, settings.lockout_duration_minutes * 60)

        await self._audit(
            user=user,
            action="user.login_failed",
            status="failure",
            request=request,
            details={"attempt": attempts},
        )

        if attempts >= settings.max_login_attempts:
            lockout_ttl = settings.lockout_duration_minutes * 60
            await self.redis.setex(RedisKeys.lockout(str(user.id)), lockout_ttl, "1")
            logger.warning(
                f"Account locked after {attempts} failed attempts: {user.email}"
            )

    async def _clear_attempts(self, user_id: str, email: str) -> None:
        """Clear failure counters after successful login."""
        await self.redis.delete(
            RedisKeys.login_attempts(user_id),
            RedisKeys.login_attempts(email),
        )

    async def _revoke_all_user_tokens(self, user_id: str) -> None:
        """
        Revoke all refresh tokens for a user (used after password change/reset).
        Scans Redis for keys matching the user's refresh tokens.
        In production with many users, consider a per-user token version counter instead.
        """
        pattern = "cybershield:refresh:*"
        async for key in self.redis.scan_iter(pattern, count=100):
            stored_user_id = await self.redis.get(key)
            if stored_user_id == user_id:
                await self.redis.delete(key)

    async def _audit(
        self,
        user: Optional[User],
        action: str,
        status: str,
        request: Optional[Request] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Write an immutable audit log entry."""
        log = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else None,
            user_role=user.role.value if user else None,
            action=action,
            status=status,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
            details=details,
        )
        self.db.add(log)
        # No explicit flush — committed with the parent transaction
