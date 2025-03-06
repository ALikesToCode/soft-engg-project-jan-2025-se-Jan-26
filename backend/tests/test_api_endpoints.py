import pytest
import uuid
from datetime import datetime, timedelta
from fastapi import status
from httpx import AsyncClient

# Authentication API Tests
@pytest.mark.asyncio
async def test_login_valid_credentials(async_client: AsyncClient):
    """Test login with valid credentials"""
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "faculty@test.com", "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    """Test login with invalid credentials"""
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "faculty@test.com", "password": "wrong_password"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient, tokens):
    """Test getting current user information"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['faculty']}"}
    
    response = await async_client.get(
        "/api/v1/auth/me",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert "id" in user
    assert "email" in user
    assert "role" in user
    assert user["role"] == "faculty"

# User API Tests
@pytest.mark.asyncio
async def test_get_users_as_admin(async_client: AsyncClient, tokens):
    """Test getting all users as admin"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['admin']}"}
    
    response = await async_client.get(
        "/api/v1/users",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0

@pytest.mark.asyncio
async def test_get_users_as_student(async_client: AsyncClient, tokens):
    """Test getting all users as student (should be forbidden)"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['student']}"}
    
    response = await async_client.get(
        "/api/v1/users",
        headers=headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Assignment API Tests
@pytest.mark.asyncio
async def test_create_assignment(async_client: AsyncClient, tokens):
    """Test creating an assignment as faculty"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['faculty']}"}
    
    # Create test assignment data
    assignment_data = {
        "title": "Test Assignment",
        "description": "This is a test assignment",
        "course_id": str(uuid.uuid4()),
        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "points": 100,
        "status": "draft",
        "submission_type": "text",
        "allow_late_submissions": True,
        "late_penalty": 10,
        "plagiarism_detection": True,
        "file_types": "pdf,doc,docx",
        "max_file_size": 5
    }
    
    response = await async_client.post(
        "/api/v1/assignments",
        headers=headers,
        json=assignment_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "assignment_id" in data
    assert data["message"] == "Assignment created successfully"
    
    return data["assignment_id"]

@pytest.mark.asyncio
async def test_create_assignment_as_student(async_client: AsyncClient, tokens):
    """Test creating an assignment as student (should be forbidden)"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['student']}"}
    
    # Create test assignment data
    assignment_data = {
        "title": "Student Test Assignment",
        "description": "This is a test assignment created by a student",
        "course_id": str(uuid.uuid4()),
        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "points": 100,
        "status": "draft",
        "submission_type": "text",
        "allow_late_submissions": True,
        "late_penalty": 10,
        "plagiarism_detection": True,
        "file_types": "pdf,doc,docx",
        "max_file_size": 5
    }
    
    response = await async_client.post(
        "/api/v1/assignments",
        headers=headers,
        json=assignment_data
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Course API Tests
@pytest.mark.asyncio
async def test_create_course(async_client: AsyncClient, tokens):
    """Test creating a course as faculty"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['faculty']}"}
    
    # Create test course data
    course_data = {
        "name": "Test Course",
        "code": "TEST101",
        "description": "This is a test course",
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
        "status": "active"
    }
    
    response = await async_client.post(
        "/api/v1/courses",
        headers=headers,
        json=course_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "course_id" in data
    assert data["message"] == "Course created successfully"
    
    return data["course_id"]

@pytest.mark.asyncio
async def test_get_courses(async_client: AsyncClient, tokens):
    """Test getting courses as faculty"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['faculty']}"}
    
    # Create a test course first
    course_id = await test_create_course(async_client, tokens)
    
    # Get courses
    response = await async_client.get(
        "/api/v1/courses",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    courses = response.json()
    assert isinstance(courses, list)
    assert len(courses) > 0
    
    # Verify the created course is in the list
    course_ids = [c["id"] for c in courses]
    assert course_id in course_ids

# FAQ API Tests
@pytest.mark.asyncio
async def test_get_faqs(async_client: AsyncClient, tokens):
    """Test getting FAQs"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['student']}"}
    
    response = await async_client.get(
        "/api/v1/faqs",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    faqs = response.json()
    assert isinstance(faqs, list)

# System Settings API Tests
@pytest.mark.asyncio
async def test_get_system_settings_as_admin(async_client: AsyncClient, tokens):
    """Test getting system settings as admin"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['admin']}"}
    
    response = await async_client.get(
        "/api/v1/system-settings",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    settings = response.json()
    assert isinstance(settings, dict)

@pytest.mark.asyncio
async def test_get_system_settings_as_student(async_client: AsyncClient, tokens):
    """Test getting system settings as student (should be forbidden)"""
    tokens_dict = await tokens
    headers = {"Authorization": f"Bearer {tokens_dict['student']}"}
    
    response = await async_client.get(
        "/api/v1/system-settings",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN 