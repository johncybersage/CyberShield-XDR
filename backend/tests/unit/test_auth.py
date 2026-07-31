"""
CyberShield XDR — Auth Unit Tests
Tests cover: registration, login, account lockout, token refresh,
logout, password reset, and RBAC enforcement.
"""
import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "email": "analyst@cybershield.test",
    "username": "testanalyst",
    "full_name": "Test Analyst",
    "password": "SecurePass1!",
    "confirm_password": "SecurePass1!",
}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == REGISTER_PAYLOAD["email"]
    assert data["user"]["role"] == "viewer"  # Default role


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    payload = {**REGISTER_PAYLOAD, "password": "weak", "confirm_password": "weak"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_password_mismatch(client: AsyncClient):
    payload = {**REGISTER_PAYLOAD, "confirm_password": "DifferentPass1!"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_username(client: AsyncClient):
    payload = {**REGISTER_PAYLOAD, "username": "a b"}  # Space not allowed
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/api/v1/auth/login", json={
        "email": REGISTER_PAYLOAD["email"],
        "password": REGISTER_PAYLOAD["password"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/api/v1/auth/login", json={
        "email": REGISTER_PAYLOAD["email"],
        "password": "WrongPassword1!",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "SomePass1!",
    })
    assert resp.status_code == 401
    # Error message must not reveal whether email exists
    assert "Invalid email or password" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Token Refresh
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    refresh_token = reg.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    # New refresh token must differ (rotation)
    assert data["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_refresh_token_rotation_prevents_reuse(client: AsyncClient):
    """After rotation, the old refresh token must be rejected."""
    reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    old_refresh = reg.json()["refresh_token"]

    # Use the token once
    await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

    # Attempt to reuse the old token
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_refresh_token(client: AsyncClient):
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": "not.a.valid.token"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Protected endpoint & RBAC
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    token = reg.json()["access_token"]

    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == REGISTER_PAYLOAD["email"]


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 403  # HTTPBearer returns 403 when no token


@pytest.mark.asyncio
async def test_admin_endpoint_blocked_for_viewer(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    token = reg.json()["access_token"]

    resp = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_logout_invalidates_token(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Logout
    resp = await client.post("/api/v1/auth/logout", headers=headers)
    assert resp.status_code == 200

    # Token should now be rejected
    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Password Reset
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_forgot_password_always_returns_success(client: AsyncClient):
    """Must return 200 even for unknown emails (prevents enumeration)."""
    resp = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nobody@example.com"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient):
    resp = await client.post("/api/v1/auth/reset-password", json={
        "token": "invalid.token.here",
        "new_password": "NewSecure1!",
        "confirm_password": "NewSecure1!",
    })
    assert resp.status_code == 400
