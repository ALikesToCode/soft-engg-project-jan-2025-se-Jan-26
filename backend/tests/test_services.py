import pytest
import uuid
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import authenticate_user, create_access_token, decode_access_token
from app.services.user_service import create_user, get_user_by_id, get_users, update_user, delete_user, UserCreate, UserUpdate
from app.services.assignment_service import AssignmentService
from app.models.user import User
from app.models.assignment import Assignment, Submission

# Authentication Service Tests
@pytest.mark.asyncio
async def test_authenticate_user_valid(db_session: AsyncSession):
    """Test user authentication with valid credentials"""
    # Create a test user first
    user_data = UserCreate(
        email="test_auth@example.com",
        name="Test Auth User",
        password="password123",
        role="student"
    )
    user_id = await create_user(db_session, user_data)
    
    # Test authentication
    user = await authenticate_user(db_session, "test_auth@example.com", "password123")
    assert user is not None
    assert user.email == "test_auth@example.com"
    assert user.role == "student"

@pytest.mark.asyncio
async def test_authenticate_user_invalid(db_session: AsyncSession):
    """Test user authentication with invalid credentials"""
    # Create a test user first
    user_data = UserCreate(
        email="test_auth_invalid@example.com",
        name="Test Auth Invalid User",
        password="password123",
        role="student"
    )
    user_id = await create_user(db_session, user_data)
    
    # Test authentication with wrong password
    user = await authenticate_user(db_session, "test_auth_invalid@example.com", "wrong_password")
    assert user is None

@pytest.mark.asyncio
async def test_token_generation_and_validation():
    """Test JWT token generation and validation"""
    # Create test user data
    user_id = str(uuid.uuid4())
    user_data = {
        "sub": user_id,  # Add the 'sub' field for the subject (user ID)
        "email": "token_test@example.com",
        "name": "Token Test User",
        "role": "faculty"
    }
    
    # Generate token
    token = create_access_token(user_data)
    assert token is not None
    
    # Validate token
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == user_id
    assert decoded["email"] == user_data["email"]
    assert decoded["role"] == user_data["role"]

# User Service Tests
@pytest.mark.asyncio
async def test_create_and_get_user(db_session: AsyncSession):
    """Test user creation and retrieval"""
    # Create a test user
    user_data = UserCreate(
        email="test_create@example.com",
        name="Test Create User",
        password="password123",
        role="student"
    )
    user_id = await create_user(db_session, user_data)
    assert user_id is not None
    
    # Get the user by ID
    user = await get_user_by_id(db_session, user_id)
    assert user is not None
    assert user.email == user_data.email
    assert user.name == user_data.name
    assert user.role == user_data.role

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    """Test user update"""
    # Create a test user
    user_data = UserCreate(
        email="test_update@example.com",
        name="Test Update User",
        password="password123",
        role="student"
    )
    user_id = await create_user(db_session, user_data)
    
    # Update the user
    update_data = UserUpdate(
        name="Updated Name",
        role="faculty"
    )
    updated_user = await update_user(db_session, user_id, update_data)
    assert updated_user is not None
    
    # Get the updated user
    user = await get_user_by_id(db_session, user_id)
    assert user.name == update_data.name
    assert user.role == update_data.role
    assert user.email == user_data.email  # Email should not change

@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    """Test user deletion"""
    # Create a test user
    user_data = UserCreate(
        email="test_delete@example.com",
        name="Test Delete User",
        password="password123",
        role="student"
    )
    user_id = await create_user(db_session, user_data)
    
    # Delete the user
    result = await delete_user(db_session, user_id)
    assert result is not None
    
    # Try to get the deleted user
    user = await get_user_by_id(db_session, user_id)
    assert user is None

# Assignment Service Tests
@pytest.mark.asyncio
async def test_create_assignment(db_session: AsyncSession):
    """Test assignment creation"""
    # Create a test user (faculty)
    faculty_data = UserCreate(
        email="faculty_test@example.com",
        name="Faculty Test User",
        password="password123",
        role="faculty"
    )
    faculty_id = await create_user(db_session, faculty_data)
    
    # Create a test assignment
    assignment_data = {
        "title": "Test Assignment",
        "description": "This is a test assignment",
        "course_id": str(uuid.uuid4()),
        "due_date": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
        "points": 100,
        "status": "draft",
        "submission_type": "text",
        "allow_late_submissions": True,
        "late_penalty": 10,
        "plagiarism_detection": True,
        "file_types": "pdf,doc,docx",
        "max_file_size": 5
    }
    
    result = await AssignmentService.create_assignment(db_session, assignment_data, faculty_id)
    assert result is not None
    assert "assignment_id" in result
    
    # Get the assignment
    assignment = await AssignmentService.get_assignment_by_id(db_session, result["assignment_id"])
    assert assignment is not None
    assert assignment.title == assignment_data["title"]
    assert assignment.description == assignment_data["description"]
    assert assignment.status == assignment_data["status"]

@pytest.mark.asyncio
async def test_update_assignment(db_session: AsyncSession):
    """Test assignment update"""
    # Create a test user (faculty)
    faculty_data = UserCreate(
        email="faculty_update@example.com",
        name="Faculty Update User",
        password="password123",
        role="faculty"
    )
    faculty_id = await create_user(db_session, faculty_data)
    
    # Create a test assignment
    assignment_data = {
        "title": "Test Assignment for Update",
        "description": "This is a test assignment for update",
        "course_id": str(uuid.uuid4()),
        "due_date": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
        "points": 100,
        "status": "draft",
        "submission_type": "text",
        "allow_late_submissions": True,
        "late_penalty": 10,
        "plagiarism_detection": True,
        "file_types": "pdf,doc,docx",
        "max_file_size": 5
    }
    
    result = await AssignmentService.create_assignment(db_session, assignment_data, faculty_id)
    assignment_id = result["assignment_id"]
    
    # Update the assignment
    update_data = {
        "title": "Updated Assignment Title",
        "points": 150,
        "status": "published"
    }
    
    success = await AssignmentService.update_assignment(db_session, assignment_id, update_data, faculty_id)
    assert success is True
    
    # Get the updated assignment
    assignment = await AssignmentService.get_assignment_by_id(db_session, assignment_id)
    assert assignment.title == update_data["title"]
    assert assignment.points == update_data["points"]
    assert assignment.status == update_data["status"]
    assert assignment.description == assignment_data["description"]  # Should not change 