import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    """
    Test that the health endpoint returns 200 OK and matches standard API response schema.
    """
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert "data" in payload
    assert payload["data"]["status"] == "online"
    assert "database" in payload["data"]
