import pytest
import uuid
import os
import shutil
import sys
from datetime import datetime, timedelta, UTC
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy import event, text
from httpx import AsyncClient
from urllib.parse import urlparse, parse_qs

# Global flag to track if patches have been applied
_PATCHES_APPLIED = False

def apply_all_patches():
    """Apply all patches for Python 3.13 compatibility only once."""
    global _PATCHES_APPLIED
    if _PATCHES_APPLIED or sys.version_info < (3, 13):
        return
    
    # Apply patches in the correct order
    from app.utils.typing_patch import apply_patch as apply_typing_patch
    from app.utils.pydantic_patch import apply_patch as apply_pydantic_patch
    from app.utils.passlib_patch import apply_patch as apply_passlib_patch
    
    apply_typing_patch()
    apply_pydantic_patch()
    apply_passlib_patch()
    
    _PATCHES_APPLIED = True

# Apply patches at module load time
apply_all_patches()

from app.database import Base, get_db
# Import all models to ensure they are registered with Base
from app.models.user import User
from app.models.assignment import Assignment, Submission
from app.models.course import Course, CourseEnrollment
from app.models.role import Role
from app.models.faq import FAQ
from app.models.system_settings import SystemSettings, Integration
from app.config import settings
from app.utils.jwt_utils import create_access_token
from main import app

# Test upload directory
TEST_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "test_uploads")
TEST_ASSIGNMENT_DIR = os.path.join(TEST_UPLOAD_DIR, "assignments")

# Create test upload directories if they don't exist
if not os.path.exists(TEST_UPLOAD_DIR):
    os.makedirs(TEST_UPLOAD_DIR)
if not os.path.exists(TEST_ASSIGNMENT_DIR):
    os.makedirs(TEST_ASSIGNMENT_DIR)

# Session-scoped schema name
@pytest.fixture(scope="session")
def test_schema():
    """Create a single test schema name for the entire test session."""
    return f"test_{uuid.uuid4().hex[:8]}"

# Session-scoped database URL
@pytest.fixture(scope="session")
def database_url():
    """Configure the database URL for testing."""
    # Check if we should use in-memory SQLite for faster tests
    if os.environ.get("TEST_USE_SQLITE", "false").lower() == "true":
        return "sqlite+aiosqlite:///:memory:"
    
    # Otherwise, use PostgreSQL with a test schema
    url = urlparse(settings.DATABASE_URL)
    query_params = parse_qs(url.query)
    
    # Remove sslmode from the URL and handle it in connect_args
    ssl_mode = query_params.pop('sslmode', ['prefer'])[0]
    cleaned_url = f"{url.scheme}://{url.netloc}{url.path}"
    if query_params:
        cleaned_url += '?' + '&'.join(f"{k}={v[0]}" for k, v in query_params.items())
    
    return cleaned_url.replace("postgres://", "postgresql+asyncpg://")

# Session-scoped engine
@pytest.fixture(scope="session")
def engine(database_url, test_schema):
    """Create a database engine once per test session."""
    is_sqlite = database_url.startswith("sqlite")
    
    # Configure engine based on database type
    if is_sqlite:
        engine = create_async_engine(
            database_url,
            echo=False,  # Set to False for faster tests
            future=True,
            poolclass=StaticPool,  # Better for in-memory testing
        )
    else:
        # For PostgreSQL, create a dedicated test schema
        engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            poolclass=NullPool,  # Avoid connection pooling in tests
            connect_args={
                # Don't include ssl parameter if using Python 3.13
                **({"ssl": True} if sys.version_info < (3, 13) else {})
            }
        )
    
    # Create schema and tables synchronously
    import asyncio
    loop = asyncio.new_event_loop()
    
    async def setup_db():
        # Create test schema if using PostgreSQL
        if not is_sqlite:
            # Create schema and set search path
            async with engine.begin() as conn:
                await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {test_schema}"))
                await conn.execute(text(f"SET search_path TO {test_schema}"))
            
            # Set search path for all connections
            @event.listens_for(engine.sync_engine, "connect")
            def set_search_path(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute(f"SET search_path TO {test_schema}")
                cursor.close()
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    
    loop.run_until_complete(setup_db())
    loop.close()
    
    return engine

# Session-scoped session factory
@pytest.fixture(scope="session")
async def session_factory(engine):
    """Create a session factory for the test database."""
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

# Function-scoped database session
@pytest.fixture
async def db_session(session_factory):
    """Create a new database session for a test."""
    session = session_factory()
    try:
        yield session
        await session.rollback()
    finally:
        await session.close()

# Override the get_db dependency
@pytest.fixture(scope="session")
def override_get_db(session_factory):
    """Override the get_db dependency for the entire test session."""
    async def _override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            await session.close()
    
    app.dependency_overrides[get_db] = _override_get_db
    return _override_get_db

# Test client with session-scoped dependency override
@pytest.fixture
def client(override_get_db):
    """Create a test client with the overridden get_db dependency."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client(override_get_db):
    """Create an async test client with the overridden get_db dependency."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

# Fixture for test users
@pytest.fixture
async def test_users(db_session):
    """Create test users for testing."""
    # Create a faculty user
    faculty_user = User(
        id=uuid.uuid4(),
        email="faculty@test.com",
        name="Test Faculty",
        hashed_password="hashed_password",
        is_google_user=False,
        role="faculty"
    )
    
    # Create a student user
    student_user = User(
        id=uuid.uuid4(),
        email="student@test.com",
        name="Test Student",
        hashed_password="hashed_password",
        is_google_user=False,
        role="student"
    )
    
    # Create a support user
    support_user = User(
        id=uuid.uuid4(),
        email="support@test.com",
        name="Test Support",
        hashed_password="hashed_password",
        is_google_user=False,
        role="support"
    )
    
    # Add users to the session
    db_session.add(faculty_user)
    db_session.add(student_user)
    db_session.add(support_user)
    await db_session.commit()
    
    # Return a dictionary of users
    return {
        "faculty": faculty_user,
        "student": student_user,
        "support": support_user
    }

# Fixture for JWT tokens
@pytest.fixture
async def tokens(test_users):
    """Create JWT tokens for test users."""
    # Ensure test_users is awaited if it's a coroutine
    users = await test_users if isinstance(test_users, object) and hasattr(test_users, "__await__") else test_users
    
    faculty_token = create_access_token({
        "email": "faculty@test.com",
        "role": "faculty",
        "sub": str(users["faculty"].id)
    })
    
    student_token = create_access_token({
        "email": "student@test.com",
        "role": "student",
        "sub": str(users["student"].id)
    })
    
    support_token = create_access_token({
        "email": "support@test.com",
        "role": "support",
        "sub": str(users["support"].id)
    })
    
    return {
        "faculty": faculty_token,
        "student": student_token,
        "support": support_token
    }

# Fixture for test assignment
@pytest.fixture
async def test_assignment(db_session, test_users):
    """Create a test assignment."""
    # Ensure test_users is awaited if it's a coroutine
    users = await test_users if isinstance(test_users, object) and hasattr(test_users, "__await__") else test_users
    
    assignment = Assignment(
        id=uuid.uuid4(),
        title="Test Assignment",
        description="This is a test assignment",
        course_id=uuid.uuid4(),
        created_by=users["faculty"].id,
        due_date=datetime.now(UTC) + timedelta(days=7),
        points=100,
        status="published",
        submission_type="file",
        allow_late_submissions=True,
        late_penalty=10,
        plagiarism_detection=True,
        file_types="pdf,doc,docx,txt",
        max_file_size=10
    )
    
    db_session.add(assignment)
    await db_session.commit()
    await db_session.refresh(assignment)
    
    return assignment

# Fixture for test submission
@pytest.fixture
async def test_submission(db_session, test_assignment, test_users):
    """Create a test submission."""
    # Ensure test_users and test_assignment are awaited if they're coroutines
    users = await test_users if isinstance(test_users, object) and hasattr(test_users, "__await__") else test_users
    assignment = await test_assignment if isinstance(test_assignment, object) and hasattr(test_assignment, "__await__") else test_assignment
    
    submission = Submission(
        id=uuid.uuid4(),
        assignment_id=assignment.id,
        student_id=users["student"].id,
        submitted_at=datetime.now(UTC),
        status="submitted",
        content="This is a test submission",
        file_name="test.pdf",
        file_type="application/pdf",
        file_size=1024
    )
    
    db_session.add(submission)
    await db_session.commit()
    await db_session.refresh(submission)
    
    return submission 