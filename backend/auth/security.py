"""
CyberShield XDR — Password & JWT Utilities
All cryptographic operations for authentication live here.

Security decisions:
- bcrypt with configurable rounds (default 12) — slow enough to resist brute force
- JWT signed with HS256 — access tokens short-lived (30 min), refresh tokens longer (7 days)
- Refresh tokens stored as SHA-256 hash in Redis, not plaintext
- Token type claim prevents refresh tokens being used as access tokens
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt as _bcrypt
from jose import JWTError, jwt

from backend.config.logging_config import get_logger
from backend.config.settings import get_settings

settings = get_settings()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Password utilities
# Uses bcrypt directly — avoids passlib/bcrypt version incompatibilities.
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt and global pepper."""
    peppered = plain + settings.bcrypt_pepper
    rounds = settings.bcrypt_rounds
    salt = _bcrypt.gensalt(rounds=rounds)
    return _bcrypt.hashpw(peppered.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against its bcrypt hash, including global pepper.
    Returns False (not raises) on any error to prevent timing oracle attacks.
    """
    try:
        peppered = plain + settings.bcrypt_pepper
        return _bcrypt.checkpw(peppered.encode(), hashed.encode())
    except Exception:
        return False


def needs_rehash(hashed: str) -> bool:
    """True if the hash was created with fewer rounds than current config."""
    try:
        stored_rounds = int(hashed.split("$")[2])
        return stored_rounds < settings.bcrypt_rounds
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT utilities
# ---------------------------------------------------------------------------

def _build_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: Optional[dict] = None,
) -> str:
    """Internal: build a signed JWT with standard + custom claims."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,          # Subject (user ID as string)
        "type": token_type,      # "access" | "refresh" | "reset"
        "iat": now,              # Issued at
        "exp": now + expires_delta,
        "jti": secrets.token_hex(16),  # Unique token ID (for revocation)
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, role: str, email: str) -> str:
    """
    Create a short-lived access token (default 30 min).
    Embeds role and email to avoid DB lookup on every request.
    """
    return _build_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
        extra_claims={"role": role, "email": email},
    )


def create_refresh_token(user_id: str) -> str:
    """
    Create a long-lived refresh token (default 7 days).
    Contains minimal claims — only used to issue new access tokens.
    """
    return _build_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def create_reset_token(user_id: str) -> str:
    """Create a short-lived password reset token (15 minutes)."""
    return _build_token(
        subject=user_id,
        token_type="reset",
        expires_delta=timedelta(minutes=15),
    )


def decode_token(token: str, expected_type: str) -> dict:
    """
    Decode and validate a JWT.

    Raises:
        JWTError: if token is invalid, expired, or wrong type
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise JWTError(f"Token decode failed: {exc}") from exc

    if payload.get("type") != expected_type:
        raise JWTError(f"Expected token type '{expected_type}', got '{payload.get('type')}'")

    return payload


# ---------------------------------------------------------------------------
# Refresh token storage helpers (Redis-backed)
# ---------------------------------------------------------------------------

def hash_refresh_token(token: str) -> str:
    """SHA-256 hash of a refresh token for safe Redis storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate a cryptographically secure random token (for reset links etc.)."""
    return secrets.token_urlsafe(nbytes)
