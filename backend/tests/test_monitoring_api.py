import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch
from fastapi import status

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client():
    async with AsyncClient(base_url="http://testserver") as ac:
        yield ac

@pytest.mark.asyncio
@patch("app.services.monitoring_service.monitoring_service.get_system_health", new_callable=AsyncMock)
async def test_get_health(mock_get_system_health, client):
    """Test the /monitoring/health endpoint with a mock."""

    # Sample mocked response
    mock_get_system_health.return_value = {
        "status": "healthy",
        "timestamp": "2024-03-05T12:00:00Z",
        "services": {
            "database": "up",
            "redis": "mock",  # This should be converted to "up (mock)" in API response
            "api": "up"
        },
        "metrics": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 73.1,
            "active_connections": 15,
            "response_time": 150,
            "error_rate": 0.5
        }
    }

    # Send request to /monitoring/health
    response = client.get("/api/v1/monitoring/health")

    # Assertions
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()

    # Validate response structure
    assert json_data["status"] == "healthy"
    assert json_data["services"]["database"] == "up"
    assert json_data["services"]["api"] == "up"
    
    # Check Redis mock override logic
    assert json_data["services"]["redis"] == "up (mock)"

@pytest.mark.asyncio
@patch("app.services.monitoring_service.monitoring_service.get_current_metrics", new_callable=AsyncMock)
async def test_get_metrics(mock_get_current_metrics, client):
    """Test the /monitoring/metrics endpoint."""

    mock_get_current_metrics.return_value = {
        "current": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 73.1,
            "active_connections": 15,
            "response_time": 150,
            "error_rate": 0.5,
            "timestamp": "2024-03-05T12:00:00Z"
        },
        "history": [
            {
            "timestamp": "2024-03-05T11:59:00Z",
            "cpu_usage": 44.8,
            "memory_usage": 62.5
            }
        ]
    }

    response = client.get("/api/v1/monitoring/metrics")
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()

    # Validate response structure
    assert "current" in json_data
    # assert "history" in json_data
    assert "cpu_usage" in json_data["current"]['current']
    # assert "active_connections" in json_data["current"]
    # assert "response_time" in json_data["current"]
    # assert "error_rate" in json_data["current"]


@pytest.mark.asyncio
@patch("app.services.monitoring_service.monitoring_service.get_system_logs", new_callable=AsyncMock)
async def test_get_logs(mock_get_system_logs, client):
    """Test the /monitoring/logs endpoint."""

    mock_get_system_logs.return_value = [
          {
            "timestamp": "2024-03-05T12:00:00Z",
            "level": "INFO",
            "message": "Application started"
            }]

    response = client.get("/api/v1/monitoring/logs", params={"level": "INFO", "limit": 10})
    assert response.status_code == 200
    assert isinstance(response.json(), list)