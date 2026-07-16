import pytest

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["product"] == "Giraffe JP — Merchant-Owned C-B-M Backend Package"
