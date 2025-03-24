import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch
from fastapi import status
from app.models.user import User
from app.utils.jwt_utils import create_access_token


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client():
    async with AsyncClient(base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def faculty_token(test_users):
    """Create a valid faculty token for testing"""
    test_users = await test_users 
    return create_access_token({
        "email": "faculty@test.com",
        "role": "faculty",
        "sub": str(test_users["faculty"].id)
    })

@pytest.fixture
def student_token(test_users):
    """Create a valid student token for testing"""
    return create_access_token({
        "email": "student@test.com",
        "role": "student",
        "sub": str(test_users["student"].id)
    })

@pytest.fixture
def support_token(test_users):
    """Create a valid support token for testing"""
    return create_access_token({
        "email": "support@test.com",
        "role": "support",
        "sub": str(test_users["faculty"].id)  # Using faculty ID for support role
    })

@pytest.mark.asyncio
@patch("app.services.system_settings_service.get_system_settings", new_callable=AsyncMock)
async def test_get_system_settings(mock_get_system_settings, client, faculty_token):
    """Test the GET /api/v1/admin/settings endpoint for different scenarios."""

    mock_get_system_settings.return_value = {
        "auth": {"jwt_expiry": 24, "oauth_provider": "google", "mfa_enabled": False},
        "notifications": {"email_frequency": "immediate", "smtp_server": "smtp.example.com"},
        "api": {"rate_limit": 100, "data_retention_days": 30},
        "integrations": [{"id": 0, "name": "string", "type": "string", "endpoint": "string", "api_key": "string", "status": "inactive"}]
    }
    headers = {"Authorization": f"Bearer {faculty_token}"}
    response = client.get("/api/v1/admin/settings", headers=headers)

    assert response.status_code == status.HTTP_200_OK
 
    json_data = response.json()
    assert isinstance(json_data, dict)
    assert "auth" in json_data
    assert "notifications" in json_data
    assert "api" in json_data
    assert "integrations" in json_data
    assert isinstance(json_data["integrations"], list)        

#PUT
@pytest.mark.asyncio
@patch("app.services.system_settings_service.update_system_settings", new_callable=AsyncMock)
async def test_update_system_settings(mock_update_system_settings, client, faculty_token):
    """Test the PUT /api/v1/admin/settings endpoint with different cases."""

    valid_settings = {
        "auth": {
            "jwt_expiry": 24,
            "oauth_provider": "google",
            "mfa_enabled": False
        },
        "notifications": {
            "email_frequency": "immediate",
            "smtp_server": "smtp.example.com"
        },
        "api": {
            "rate_limit": 100,
            "data_retention_days": 30
        },
        "integrations": [
            {
                "id": 0,
                "name": "string",
                "type": "string",
                "endpoint": "string",
                "api_key": "string",
                "status": "inactive"
            }
        ]
    }

    invalid_settings = {
        "auth": {
            "jwt_expiry": "invalid_value",  # Should be an integer
            "oauth_provider": 123  # Should be a string
        }
    }

    admin_headers = {"Authorization": f"Bearer {faculty_token}"}
    #Valid settings with admin token (200 OK)
    mock_update_system_settings.return_value = {"message": "Settings updated successfully"}
    response = client.put("/api/v1/admin/settings", json=valid_settings, headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK

    #Invalid settings data (422 Unprocessable Entity)
    response = client.put("/api/v1/admin/settings", json=invalid_settings, headers=admin_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
