import pytest
import json
import uuid
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_notifications(client: TestClient, tokens):
    # Valid token scenario
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['student']}"}

    response = await client.get(
        "/api/v1/notifications",
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

    # Invalid token scenario
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get(
        "/api/v1/notifications",
        headers=headers
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_mark_notification_as_read(client: TestClient, tokens):
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['student']}"}

    # Create a notification for testing (mock)
    notification_id = str(uuid.uuid4())

    # Valid mark as read
    response = await client.put(
        f"/api/v1/notifications/{notification_id}/read",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK

    # Mark as read with different user token
    headers = {"Authorization": f"Bearer {token_data['support']}"}
    response = await client.put(
        f"/api/v1/notifications/{notification_id}/read",
        headers=headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Invalid notification ID
    invalid_notification_id = str(uuid.uuid4())
    response = await client.put(
        f"/api/v1/notifications/{invalid_notification_id}/read",
        headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_websocket_notifications(client: TestClient, tokens):
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens

    # Successful WebSocket connection with valid token
    async with client.websocket_connect(
        f"/ws/notifications?token={token_data['student']}"
    ) as websocket:
        assert websocket is not None

    # WebSocket connection with invalid token
    with pytest.raises(Exception):
        await client.websocket_connect(
            f"/ws/notifications?token=invalid_token"
        )

    # WebSocket connection without token
    with pytest.raises(Exception):
        await client.websocket_connect(
            "/ws/notifications"
        )


@pytest.mark.asyncio
async def test_real_time_notification_delivery(client: TestClient, tokens):
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens

    async with client.websocket_connect(
        f"/ws/notifications?token={token_data['student']}"
    ) as websocket:
        # Mock events for notifications
        await websocket.send_json({"type": "assignment_created", "message": "New assignment available"})
        response = await websocket.receive_json()
        assert response["message"] == "New assignment available"

        await websocket.send_json({"type": "course_announcement", "message": "New course announcement"})
        response = await websocket.receive_json()
        assert response["message"] == "New course announcement"

        await websocket.send_json({"type": "system_alert", "message": "System maintenance at midnight"})
        response = await websocket.receive_json()
        assert response["message"] == "System maintenance at midnight"

        # Simulate connection interruption
        await websocket.close()
        with pytest.raises(Exception):
            await websocket.receive_json()
