"""
CyberShield XDR — Security Utility Tests
Tests for password hashing and JWT token creation/validation.
"""

import pytest
from jose import JWTError

from backend.auth.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    generate_secure_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def test_hash_password_produces_bcrypt_hash():
    hashed = hash_password("TestPass1!")
    assert hashed.startswith("$2b$")


def test_verify_password_correct():
    hashed = hash_password("TestPass1!")
    assert verify_password("TestPass1!", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("TestPass1!")
    assert verify_password("WrongPass1!", hashed) is False


def test_verify_password_does_not_raise_on_invalid_hash():
    """Must return False, not raise, to prevent timing oracle."""
    assert verify_password("anything", "not-a-valid-hash") is False


def test_different_passwords_produce_different_hashes():
    h1 = hash_password("TestPass1!")
    h2 = hash_password("TestPass1!")
    assert h1 != h2  # bcrypt uses random salt


# ---------------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------------

def test_access_token_decode():
    token = create_access_token("user-123", "admin", "admin@test.com")
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"
    assert payload["email"] == "admin@test.com"
    assert payload["type"] == "access"


def test_refresh_token_decode():
    token = create_refresh_token("user-456")
    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"


def test_reset_token_decode():
    token = create_reset_token("user-789")
    payload = decode_token(token, expected_type="reset")
    assert payload["sub"] == "user-789"
    assert payload["type"] == "reset"


def test_wrong_token_type_raises():
    """Refresh token must not be accepted as access token."""
    refresh = create_refresh_token("user-123")
    with pytest.raises(JWTError):
        decode_token(refresh, expected_type="access")


def test_tampered_token_raises():
    token = create_access_token("user-123", "admin", "admin@test.com")
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(JWTError):
        decode_token(tampered, expected_type="access")


def test_token_has_unique_jti():
    """Each token must have a unique JTI for blacklisting."""
    t1 = create_access_token("user-1", "viewer", "a@test.com")
    t2 = create_access_token("user-1", "viewer", "a@test.com")
    p1 = decode_token(t1, "access")
    p2 = decode_token(t2, "access")
    assert p1["jti"] != p2["jti"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_hash_refresh_token_is_deterministic():
    token = "some.refresh.token"
    assert hash_refresh_token(token) == hash_refresh_token(token)


def test_hash_refresh_token_different_inputs():
    assert hash_refresh_token("token-a") != hash_refresh_token("token-b")


def test_generate_secure_token_length():
    token = generate_secure_token(32)
    assert len(token) > 0
    # URL-safe base64: 32 bytes → ~43 chars
    assert len(token) >= 40


def test_generate_secure_token_uniqueness():
    tokens = {generate_secure_token() for _ in range(100)}
    assert len(tokens) == 100  # All unique
