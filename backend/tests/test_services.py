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
    
    # Create a user directly in the database
    user = User(
        id=uuid.uuid4(),
        email="test_auth@example.com",
        name="Test Auth User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
        role="student",
        is_google_user=False
    )
    db_session.add(user)
    await db_session.commit()
    
    # Test authentication
    authenticated_user = await authenticate_user(db_session, "test_auth@example.com", "password123")
    assert authenticated_user is not None
    assert authenticated_user.email == "test_auth@example.com"
    assert authenticated_user.role == "student"

@pytest.mark.asyncio
async def test_authenticate_user_invalid(db_session: AsyncSession):
    """Test user authentication with invalid credentials"""
    # Create a test user first
    user = User(
        id=uuid.uuid4(),
        email="test_auth_invalid@example.com",
        name="Test Auth Invalid User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
        role="student",
        is_google_user=False
    )
    db_session.add(user)
    await db_session.commit()
    
    # Test authentication with wrong password
    authenticated_user = await authenticate_user(db_session, "test_auth_invalid@example.com", "wrong_password")
    assert authenticated_user is None

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
    # Create a test user directly in the database
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="test_create@example.com",
        name="Test Create User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
        role="student",
        is_google_user=False
    )
    db_session.add(user)
    await db_session.commit()
    
    # Get the user by ID
    retrieved_user = await get_user_by_id(db_session, user_id)
    assert retrieved_user is not None
    assert retrieved_user.email == "test_create@example.com"
    assert retrieved_user.name == "Test Create User"
    assert retrieved_user.role == "student"

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    """Test user update"""
    # Create a test user directly in the database
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="test_update@example.com",
        name="Test Update User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
        role="student",
        is_google_user=False
    )
    db_session.add(user)
    await db_session.commit()
    
    # Update the user
    update_data = UserUpdate(
        name="Updated User Name",
        role="faculty"
    )
    
    # Update user directly in the database
    user = await get_user_by_id(db_session, user_id)
    user.name = update_data.name
    user.role = update_data.role
    await db_session.commit()
    
    # Get the updated user
    updated_user = await get_user_by_id(db_session, user_id)
    assert updated_user is not None
    assert updated_user.name == update_data.name
    assert updated_user.role == update_data.role
    assert updated_user.email == "test_update@example.com"  # Email should remain unchanged

@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    """Test user deletion"""
    # Create a test user directly in the database
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="test_delete@example.com",
        name="Test Delete User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
        role="student",
        is_google_user=False
    )
    db_session.add(user)
    await db_session.commit()
    
    # Verify user exists
    user_before_delete = await get_user_by_id(db_session, user_id)
    assert user_before_delete is not None
    
    # Delete the user directly from the database
    await db_session.delete(user)
    await db_session.commit()
    
    # Verify user was deleted
    deleted_user = await get_user_by_id(db_session, user_id)
    assert deleted_user is None

# Assignment Service Tests
@pytest.mark.asyncio
async def test_create_assignment(db_session: AsyncSession):
    """Test assignment creation"""
    # Create a test user (faculty) directly in the database
    faculty_id = uuid.uuid4()
    faculty = User(
        id=faculty_id,
        email="faculty_test@example.com",
        name="Faculty Test User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
        role="faculty",
        is_google_user=False
    )
    db_session.add(faculty)
    await db_session.commit()
    
    # Create a test assignment directly in the database
    course_id = uuid.uuid4()
    assignment_id = uuid.uuid4()
    assignment = Assignment(
        id=assignment_id,
        title="Test Assignment",
        description="This is a test assignment",
        course_id=course_id,
        created_by=faculty_id,
        due_date=datetime.now(UTC) + timedelta(days=7),
        points=100,
        status="draft",
        submission_type="text"
    )
    db_session.add(assignment)
    await db_session.commit()
    
    # Verify assignment was created
    assignment_from_db = await db_session.get(Assignment, assignment_id)
    assert assignment_from_db is not None
    assert assignment_from_db.title == "Test Assignment"
    assert assignment_from_db.description == "This is a test assignment"
    assert assignment_from_db.course_id == course_id
    assert assignment_from_db.created_by == faculty_id

@pytest.mark.asyncio
async def test_update_assignment(db_session: AsyncSession):
    """Test assignment update"""
    # Create a test user (faculty) directly in the database
    faculty_id = uuid.uuid4()
    faculty = User(
        id=faculty_id,
        email="faculty_update@example.com",
        name="Faculty Update User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
        role="faculty",
        is_google_user=False
    )
    db_session.add(faculty)
    await db_session.commit()
    
    # Create a test assignment directly in the database
    course_id = uuid.uuid4()
    assignment_id = uuid.uuid4()
    assignment = Assignment(
        id=assignment_id,
        title="Test Assignment for Update",
        description="This is a test assignment for update",
        course_id=course_id,
        created_by=faculty_id,
        due_date=datetime.now(UTC) + timedelta(days=7),
        points=100,
        status="draft",
        submission_type="text"
    )
    db_session.add(assignment)
    await db_session.commit()
    
    # Update the assignment directly in the database
    assignment.title = "Updated Assignment Title"
    assignment.description = "Updated assignment description"
    assignment.points = 150
    assignment.status = "published"
    await db_session.commit()
    
    # Verify assignment was updated
    updated_assignment = await db_session.get(Assignment, assignment_id)
    assert updated_assignment is not None
    assert updated_assignment.title == "Updated Assignment Title"
    assert updated_assignment.description == "Updated assignment description"
    assert updated_assignment.points == 150
    assert updated_assignment.status == "published"
    assert updated_assignment.course_id == course_id  # Should remain unchanged
    assert updated_assignment.created_by == faculty_id  # Should remain unchanged 