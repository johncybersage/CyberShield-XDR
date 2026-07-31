"""
CyberShield XDR — Authentication Endpoints
Thin controllers — all logic delegated to AuthService.

Rate limiting is enforced at the Nginx layer (10 req/min on /auth/*).
Additional in-process rate limiting via Redis for defense-in-depth.
"""
from typing import Annotated, Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import CurrentUser
from backend.config.settings import get_settings
from backend.database.redis_client import RedisKeys, get_redis
from backend.database.session import get_db
from backend.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from backend.services.auth_service import AuthService

router = APIRouter()
settings = get_settings()


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
) -> AuthService:
    return AuthService(db=db, redis=redis)


# ---------------------------------------------------------------------------
# In-process rate limiter (defense-in-depth on top of Nginx)
# ---------------------------------------------------------------------------

async def check_auth_rate_limit(request: Request, redis: aioredis.Redis) -> None:
    """Allow max 10 auth attempts per IP per minute."""
    ip = request.client.host if request.client else "unknown"
    key = RedisKeys.rate_limit(ip, "auth")
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)
    if count > settings.auth_rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please wait before trying again.",
            headers={"Retry-After": "60"},
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    data: RegisterRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
):
    """
    Create a new user account and return JWT tokens.
    Default role is 'viewer' — admin must promote to analyst/admin.
    """
    await check_auth_rate_limit(request, redis)
    return await service.register(data, request)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT tokens",
)
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
):
    """
    Authenticate with email + password.
    Returns access token (30 min) and sets refresh token in HttpOnly cookie.
    Account locks after 5 failed attempts.
    """
    await check_auth_rate_limit(request, redis)
    token_data = await service.login(data, request)
    response.set_cookie(
        key="refresh_token",
        value=token_data.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60, # 7 days
    )
    return token_data


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using refresh token",
)
async def refresh_token(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    data: Optional[RefreshRequest] = None,
):
    """
    Exchange a valid refresh token (from cookie or body) for a new access + refresh token pair.
    The old refresh token is immediately invalidated (rotation).
    """
    token_value = (data.refresh_token if data else None) or request.cookies.get("refresh_token")
    if not token_value:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    refresh_data = RefreshRequest(refresh_token=token_value)
    token_data = await service.refresh(refresh_data)
    
    response.set_cookie(
        key="refresh_token",
        value=token_data.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )
    return token_data


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Invalidate current session",
)
async def logout(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Optional[str] = None,
):
    """
    Blacklist the current access token and optionally revoke the refresh token.
    Pass refresh_token in request body or cookie to fully invalidate the session.
    """
    auth_header = request.headers.get("Authorization", "")
    access_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    token_value = refresh_token or request.cookies.get("refresh_token")
    
    await service.logout(current_user, access_token, token_value, request)
    response.delete_cookie("refresh_token")
    
    return MessageResponse(message="Successfully logged out")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request a password reset email",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
):
    """
    Send a password reset link to the provided email.
    Always returns success to prevent email enumeration.
    """
    await check_auth_rate_limit(request, redis)
    reset_token = await service.forgot_password(data.email)

    if reset_token:
        # In production: send email with reset link
        # For now: log token (remove in production!)
        from backend.config.logging_config import get_logger
        get_logger(__name__).info(
            f"[DEV ONLY] Reset token for {data.email}: {reset_token}"
        )

    return MessageResponse(
        message="If that email is registered, you will receive a reset link shortly."
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password using reset token",
)
async def reset_password(
    data: ResetPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Reset password using the token received via email. Token is single-use."""
    await service.reset_password(data)
    return MessageResponse(message="Password reset successfully. Please log in.")


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password (authenticated)",
)
async def change_password(
    data: ChangePasswordRequest,
    request: Request,
    current_user: CurrentUser,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Change password for the currently authenticated user. Requires current password."""
    await service.change_password(current_user, data, request)
    return MessageResponse(message="Password changed successfully. Please log in again.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def get_me(current_user: CurrentUser):
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)
