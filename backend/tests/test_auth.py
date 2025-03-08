import pytest
import requests
from fastapi import status

BASE_URL = "http://127.0.0.1:8000"
LOGIN_ENDPOINT = "/api/v1/auth/login"
GOOGLE_LOGIN_ENDPOINT = "/api/v1/auth/login/google"
GOOGLE_CALLBACK_ENDPOINT = "/api/v1/auth/callback"
USER_INFO_ENDPOINT = "/api/v1/auth/me"
LOGOUT_ENDPOINT = "/api/v1/auth/logout"
REFRESH_TOKEN_ENDPOINT = "/api/v1/auth/refresh"
SET_PASSWORD_ENDPOINT = "/api/v1/auth/set-password"
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

@pytest.mark.parametrize("payload, expected_status", [
    ({"username": "student@ds.study.iitm.ac.in", "password": "student123"}, status.HTTP_200_OK),
    ({"username": "invalid@ds.study.iitm.ac.in", "password": "student123"}, status.HTTP_400_BAD_REQUEST),
    ({"username": "student@ds.study.iitm.ac.in", "password": "wrongpassword"}, status.HTTP_400_BAD_REQUEST),
    ({"username": None, "password": None}, status.HTTP_422_UNPROCESSABLE_ENTITY),
])
def test_email_password_login(payload, expected_status):
    """Test the email/password login endpoint."""
    response = requests.post(
        BASE_URL + LOGIN_ENDPOINT,
        data=payload,
        headers=HEADERS,
        timeout=10
    )

    print(f"Test case: {payload['username']} | Expected: {expected_status}, Got: {response.status_code}")
    print(response.text)  

    assert response.status_code == expected_status


@pytest.mark.parametrize("endpoint, params, expected_status", [
    (GOOGLE_LOGIN_ENDPOINT, None, status.HTTP_200_OK),
    (GOOGLE_CALLBACK_ENDPOINT, {"state": "UWfmFlFEpUFKjbB3cKMcpmHF9RKgb9%26code%3D4%252F0AQSTgQGeAGuEo5oRzC8-i77LP9NPoKQ9Eh09aJJsjqyUMMr1xHX1FH3AZOF5Ws8HkwFteA%26scope%3Demail%2Bprofile%2Bhttps%253A%252F%252Fwww.googleapis.com%252Fauth%252Fuserinfo.email%2Bhttps%253A%252F%252Fwww.googleapis.com%252Fauth%252Fuserinfo.profile%2Bopenid%26authuser%3D0%26hd%3Dds.study.iitm.ac.in%26prompt%3Dnone+HTTP%2F1.1 HTTP/1.1"}, status.HTTP_307_TEMPORARY_REDIRECT),
    (GOOGLE_CALLBACK_ENDPOINT, {"state": "invalid_oauth_code"}, status.HTTP_400_BAD_REQUEST),
])
def test_google_auth(endpoint, params, expected_status):
    """Test the Google OAuth login and callback endpoints."""
    response = requests.get(
        BASE_URL + endpoint,
        params=params,
        timeout=10
    )

    print(f"Test case: {endpoint} | Params: {params} | Expected: {expected_status}, Got: {response.status_code}")
    print(response.text)  
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, expected_status", [
    ("valid_token", status.HTTP_200_OK),
    ("invalid_token", status.HTTP_401_UNAUTHORIZED),
    (None, status.HTTP_401_UNAUTHORIZED),
])
def test_user_info(payload, expected_status):
    """Test the /auth/me endpoint."""
    headers = {"Authorization": f"Bearer {payload}"} if payload else {}
    response = requests.get(BASE_URL + USER_INFO_ENDPOINT, headers=headers, timeout=10)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, expected_status", [
    ("valid_token", status.HTTP_200_OK),
    ("invalid_token", status.HTTP_401_UNAUTHORIZED),
    (None, status.HTTP_401_UNAUTHORIZED),
])
def test_logout(payload, expected_status):
    """Test the /auth/logout endpoint."""
    headers = {"Authorization": f"Bearer {payload}"} if payload else {}
    response = requests.get(BASE_URL + LOGOUT_ENDPOINT, headers=headers, timeout=10)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, expected_status", [
    ("valid_refresh_token", status.HTTP_200_OK),
    ("expired_token", status.HTTP_401_UNAUTHORIZED),
    ("invalid_token", status.HTTP_401_UNAUTHORIZED),
])
def test_refresh_token(payload, expected_status):
    """Test the /auth/refresh endpoint."""
    headers = {"Authorization": f"Bearer {payload}"} if payload else {}
    response = requests.post(BASE_URL + REFRESH_TOKEN_ENDPOINT, headers=headers, timeout=10)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, expected_status", [
    ({"token": "valid_token", "password": "NewPass123!"}, status.HTTP_200_OK),
    ({"token": "valid_token", "password": "123"}, status.HTTP_400_BAD_REQUEST),
    ({"token": "invalid_token", "password": "NewPass123!"}, status.HTTP_401_UNAUTHORIZED),
])
def test_set_password(payload, expected_status):
    """Test the /auth/set-password endpoint."""
    headers = {"Authorization": f"Bearer {payload['token']}"} if payload['token'] else {}
    response = requests.post(BASE_URL + SET_PASSWORD_ENDPOINT, json={"password": payload["password"]}, headers=headers, timeout=10)
    assert response.status_code == expected_status
