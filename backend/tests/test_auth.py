import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.models.user import User
from app.utils.jwt_utils import create_access_token
from main import app

# Test constants
BASE_URL = "/api/v1/auth"
LOGIN_ENDPOINT = f"{BASE_URL}/login"
GOOGLE_LOGIN_ENDPOINT = f"{BASE_URL}/login/google"
GOOGLE_CALLBACK_ENDPOINT = f"{BASE_URL}/callback"
USER_INFO_ENDPOINT = f"{BASE_URL}/me"
LOGOUT_ENDPOINT = f"{BASE_URL}/logout"
REFRESH_TOKEN_ENDPOINT = f"{BASE_URL}/refresh"
SET_PASSWORD_ENDPOINT = f"{BASE_URL}/set-password"
RESET_PASSWORD_ENDPOINT = f"{BASE_URL}/reset-password"
VERIFY_EMAIL_ENDPOINT = f"{BASE_URL}/verify-email"

# Test fixtures
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client():
    async with AsyncClient(base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def faculty_token(test_users):
    """Create a valid faculty token for testing"""
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

# Email/Password Login Tests
@pytest.mark.parametrize("payload, expected_status", [
    ({"username": "faculty@test.com", "password": "faculty123"}, status.HTTP_200_OK),
    ({"username": "invalid@test.com", "password": "faculty123"}, status.HTTP_400_BAD_REQUEST),
    ({"username": "faculty@test.com", "password": "wrongpassword"}, status.HTTP_400_BAD_REQUEST),
    ({"username": None, "password": None}, status.HTTP_422_UNPROCESSABLE_ENTITY),
])
@patch('app.routes.auth.authenticate_user')
async def test_email_password_login(mock_authenticate, payload, expected_status, client):
    """Test the email/password login endpoint with various inputs"""
    # Mock authentication based on expected status
    if expected_status == status.HTTP_200_OK:
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = payload["username"]
        mock_user.role = "faculty"
        mock_authenticate.return_value = mock_user
    else:
        mock_authenticate.return_value = None if expected_status == status.HTTP_400_BAD_REQUEST else mock_authenticate.return_value
    
    # Send login request
    response = client.post(
        LOGIN_ENDPOINT,
        data=payload if all(payload.values()) else {},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check response
    assert response.status_code == expected_status
    
    # Verify successful login returns tokens
    if expected_status == status.HTTP_200_OK:
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

# Google OAuth Tests
@pytest.mark.parametrize("endpoint, params, expected_status, mock_return", [
    (GOOGLE_LOGIN_ENDPOINT, None, status.HTTP_200_OK, None),
    (GOOGLE_CALLBACK_ENDPOINT, {"state": "valid_state", "code": "valid_code"}, status.HTTP_307_TEMPORARY_REDIRECT, {"id": "google_user_id", "email": "user@gmail.com", "name": "Test User"}),
    (GOOGLE_CALLBACK_ENDPOINT, {"state": "invalid_state"}, status.HTTP_400_BAD_REQUEST, None),
])
@patch('app.routes.auth.get_google_user_info')
async def test_google_auth(mock_google_info, endpoint, params, expected_status, mock_return, client):
    """Test the Google OAuth login and callback endpoints"""
    # Mock Google user info response
    mock_google_info.return_value = mock_return
    
    # Send request
    response = client.get(endpoint, params=params)
    
    # Check response
    assert response.status_code == expected_status
    
    # For successful callback, verify redirect
    if endpoint == GOOGLE_CALLBACK_ENDPOINT and expected_status == status.HTTP_307_TEMPORARY_REDIRECT:
        assert "Location" in response.headers
        assert response.headers["Location"].startswith("/")

# User Info Tests
@pytest.mark.asyncio
async def test_user_info_success(client, faculty_token):
    """Test successful user info retrieval"""
    # Send request with valid token
    response = client.get(
        USER_INFO_ENDPOINT,
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "role" in data
    assert data["role"] == "faculty"

@pytest.mark.asyncio
async def test_user_info_invalid_token(client):
    """Test user info with invalid token"""
    # Send request with invalid token
    response = client.get(
        USER_INFO_ENDPOINT,
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_user_info_missing_token(client):
    """Test user info with missing token"""
    # Send request without token
    response = client.get(USER_INFO_ENDPOINT)
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Logout Tests
@pytest.mark.asyncio
async def test_logout_success(client, faculty_token):
    """Test successful logout"""
    # Send logout request with valid token
    response = client.post(
        LOGOUT_ENDPOINT,
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "logged out" in data["message"].lower()

@pytest.mark.asyncio
async def test_logout_invalid_token(client):
    """Test logout with invalid token"""
    # Send logout request with invalid token
    response = client.post(
        LOGOUT_ENDPOINT,
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Token Refresh Tests
@pytest.mark.asyncio
@patch('app.routes.auth.verify_refresh_token')
async def test_refresh_token_success(mock_verify, client):
    """Test successful token refresh"""
    # Mock token verification
    mock_verify.return_value = {"sub": "user-id", "email": "user@test.com", "role": "faculty"}
    
    # Send refresh request
    response = client.post(
        REFRESH_TOKEN_ENDPOINT,
        headers={"Authorization": "Bearer valid_refresh_token"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
@patch('app.routes.auth.verify_refresh_token')
async def test_refresh_token_expired(mock_verify, client):
    """Test refresh with expired token"""
    # Mock token verification to raise exception
    mock_verify.side_effect = Exception("Token expired")
    
    # Send refresh request
    response = client.post(
        REFRESH_TOKEN_ENDPOINT,
        headers={"Authorization": "Bearer expired_token"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Password Management Tests
@pytest.mark.asyncio
@patch('app.routes.auth.get_user_by_id')
@patch('app.routes.auth.update_user_password')
async def test_set_password_success(mock_update, mock_get_user, client, faculty_token):
    """Test successful password update"""
    # Mock user retrieval
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_get_user.return_value = mock_user
    
    # Mock password update
    mock_update.return_value = True
    
    # Send password update request
    response = client.post(
        SET_PASSWORD_ENDPOINT,
        headers={"Authorization": f"Bearer {faculty_token}"},
        json={"password": "NewSecurePassword123!"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "password updated" in data["message"].lower()

@pytest.mark.asyncio
async def test_set_password_weak(client, faculty_token):
    """Test password update with weak password"""
    # Send password update request with weak password
    response = client.post(
        SET_PASSWORD_ENDPOINT,
        headers={"Authorization": f"Bearer {faculty_token}"},
        json={"password": "123"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
@patch('app.routes.auth.send_password_reset_email')
async def test_reset_password_request(mock_send_email, client):
    """Test password reset request"""
    # Mock email sending
    mock_send_email.return_value = True
    
    # Send password reset request
    response = client.post(
        RESET_PASSWORD_ENDPOINT,
        json={"email": "user@test.com"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "reset link" in data["message"].lower()

# Email Verification Tests
@pytest.mark.asyncio
@patch('app.routes.auth.verify_email_token')
@patch('app.routes.auth.update_user_verified')
async def test_verify_email_success(mock_update, mock_verify, client):
    """Test successful email verification"""
    # Mock token verification
    mock_verify.return_value = {"sub": "user-id", "email": "user@test.com"}
    
    # Mock user update
    mock_update.return_value = True
    
    # Send verification request
    response = client.get(
        f"{VERIFY_EMAIL_ENDPOINT}?token=valid_verification_token"
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "verified" in data["message"].lower()

@pytest.mark.asyncio
@patch('app.routes.auth.verify_email_token')
async def test_verify_email_invalid_token(mock_verify, client):
    """Test email verification with invalid token"""
    # Mock token verification to raise exception
    mock_verify.side_effect = Exception("Invalid token")
    
    # Send verification request
    response = client.get(
        f"{VERIFY_EMAIL_ENDPOINT}?token=invalid_token"
    )
    
    # Check response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
