import pytest
import json
import uuid
from fastapi import status
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_faq(client: TestClient, tokens):
    # can be created by anyone
    # only login is required
    # role doesn't matter here

    for role in ["student", "faculty", "support"]:
        token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
        headers = {"Authorization": f"Bearer {token_data[role]}"}

    # Create a new FAQ
    faq_data = {
        "question": "How do I submit an assignment?",
        "answer": "You can submit your assignment by navigating to the assignment page and clicking the 'Submit' button.",
        "category_id": "general",
        "priority": 10
    }

    # Send request to create FAQ
    response = await client.post(
        "api/v1/faqs",
        headers=headers,
        json=faq_data
    ) if isinstance(client, AsyncClient) else client.post(
        "api/v1/faqs",
        headers=headers,
        json=faq_data
    )

    # Check response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    # assert data["question"] == "How do I submit an assignment?"
    # assert data["category_id"] == "general"
    # assert data["priority"] == 10
    
    # Store FAQ ID for later tests
    return data["id"]


@ pytest.mark.asyncio
async def test_get_faqs(client: TestClient, tokens):
    faq_id = await test_create_faq(client, tokens)

    for role in ["student", "faculty", "support"]:
        token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
        headers = {"Authorization": f"Bearer {token_data[role]}"}

        response = await client.get(
            "api/v1/faqs",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any(faq["id"] == faq_id for faq in data)

@ pytest.mark.asyncio
async def test_get_faq_by_id(client: TestClient, tokens):
    faq_id = await test_create_faq(client, tokens)

    for role in ["student", "faculty", "support"]:
        token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
        headers = {"Authorization": f"Bearer {token_data[role]}"}

        response = await client.get(
            f"api/v1/faqs/{faq_id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == faq_id

@ pytest.mark.asyncio
async def test_update_faq(client: TestClient, tokens):
    faq_id = await test_create_faq(client, tokens)  

    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    update_data = {"question": "How do I update an assignment?"}

    response = await client.put(
        f"api/v1/faqs/{faq_id}",
        headers=headers,
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["question"] == "How do I update an assignment?"

@ pytest.mark.asyncio
async def test_delete_faq(client: TestClient, tokens):
    faq_id = await test_create_faq(client, tokens)

    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['support']}"}

    response = await client.delete(
        f"api/v1/faqs/{faq_id}",
        headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get(
        f"api/v1/faqs/{faq_id}",
        headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND