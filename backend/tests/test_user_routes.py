import pytest
import json
import uuid
from fastapi import status
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from httpx import AsyncClient
# from app.main import app

@pytest.mark.asyncio
async def test_create_user(client: TestClient, tokens):
    # Login as support
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    # Create a new user
    user_data = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "role": "student"
    }

    # Send request to create user
    response = await client.post(
        "api/v1/users/add",
        headers=headers,
        json=user_data
    ) if isinstance(client, AsyncClient) else client.post(
        "api/v1/users/add",
        headers=headers,
        json=user_data
    )

    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "user_id" in data
    assert data["message"] == "User created successfully"

    # Store user ID for later tests
    return data["user_id"]

@pytest.mark.asyncio
async def test_create_user_invalid_role(client: TestClient, tokens):
    # Login as support
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    # Create a new user with invalid role
    invaild_data = {
        "name": "",
        "email": "invalid-email",
        "password": "123"
    }

    response = await client.post(
        "api/v1/users/add",
        headers=headers,
        json=invaild_data
    ) if isinstance(client, AsyncClient) else client.post(
        "api/v1/users/add",
        headers=headers,
        json=invaild_data
    )

    # Check response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["msg"] == "value_error.missing"
    assert data["detail"][1]["msg"] == "value_error.email"
    assert data["detail"][2]["msg"] == "value_error.any_str.min_length"

@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: TestClient, tokens):
    # Login as support
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    # Create a new user with duplicate email
    user_data = {
        "name": "Duplicate User",
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "role": "student"
    }

    response = await client.post(
        "api/v1/users/add",
        headers=headers,
        json=user_data
    ) if isinstance(client, AsyncClient) else client.post(
        "api/v1/users/add",
        headers=headers,
        json=user_data
    )

    # Check response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "User with this email already exists"

@pytest.mark.asyncio
async def test_get_users(client: TestClient, tokens):
    # Login as support
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    user_id = await test_create_user(client, tokens)

    # Get users
    response = await client.get(
        "/api/v1/users",
        headers=headers
    ) if isinstance(client, AsyncClient) else client.get(
        "/api/v1/users",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1

    # Verify the created user is in the list
    user_ids = [u["id"] for u in users]
    assert user_id in user_ids

@pytest.mark.asyncio
async def test_get_user(client: TestClient, tokens):
    # Login as support
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    user_id = await test_create_user(client, tokens)

    # Get the user
    response = await client.get(
        f"/api/v1/users/{user_id}",
        headers=headers
    ) if isinstance(client, AsyncClient) else client.get(
        f"/api/v1/users/{user_id}",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["id"] == user_id
    assert user["name"] == "New User"

@pytest.mark.asyncio
async def test_update_user(client: TestClient, tokens):
    # Login as support
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    user_id = await test_create_user(client, tokens)

    # Update data
    update_data = {
        "name":"Updated User"
    }

    # Send request to update user
    response = client.put(
        f"/api/v1/users/{user_id}",
        headers=headers,
        json=update_data
    ) if isinstance(client, AsyncClient) else client.put(
        f"/api/v1/users/{user_id}",
        headers=headers,
        json=update_data
    )

    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "User updated successfully"

    # verify the updated user
    response = await client.get(
        f"/api/v1/users/{user_id}",
        headers=headers
    )
    updated_user = response.json()
    assert updated_user["name"] == update_data["name"]

    # response = await async_client.put(
    #     f"/users/{test_user_id}",
    #     json={"name": "Updated User"},
    #     headers=support_auth_headers
    # )
    # assert response.status_code == 200
    # assert response.json()["name"] == "Updated User"


@pytest.mark.asyncio
async def test_delete_user(client: TestClient, tokens):
    # Login as support
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    user_id = await test_create_user(client, tokens)

    # Delete the user
    response = await client.delete(
        f"/api/v1/users/{user_id}",
        headers=headers
    ) if isinstance(client, AsyncClient) else client.delete(
        f"/api/v1/users/{user_id}",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "User deleted successfully"

    # Verify the user is deleted
    response = await client.get(
        f"/api/v1/users/{user_id}",
        headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # response = await async_client.delete(f"/users/{test_user_id}", headers=support_auth_headers)
    # assert response.status_code == 200
    # assert response.json()["message"] == "User deleted"


@pytest.mark.asyncio
async def test_verify_email(async_client: AsyncClient, support_auth_headers):
    response = await async_client.post(
        "/users/verify-email",
        json={"email": "newuser@example.com"},
        headers=support_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified"


@pytest.mark.asyncio
async def test_reset_password(async_client: AsyncClient, support_auth_headers):
    response = await async_client.post(
        "/users/reset-password",
        json={
            "email": "newuser@example.com",
            "new_password": "NewSecurePassword123!"
        },
        headers=support_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset"
