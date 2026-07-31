import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trigger_scan(client: AsyncClient, token_analyst: str):
    headers = {"Authorization": f"Bearer {token_analyst}"}
    payload = {
        "target_ip": "192.168.1.100",
        "scan_type": "quick"
    }
    
    response = await client.post("/api/v1/scans", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["target_ip"] == "192.168.1.100"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_scans(client: AsyncClient, token_analyst: str):
    headers = {"Authorization": f"Bearer {token_analyst}"}
    response = await client.get("/api/v1/scans", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
