import pytest
import uuid
import os
import shutil
from datetime import datetime, timedelta, UTC
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import event, text
from httpx import AsyncClient
from urllib.parse import urlparse, parse_qs

# Apply Pydantic v1 patch for Python 3.13 compatibility
from app.utils.pydantic_patch import apply_patch
apply_patch()

# Apply passlib bcrypt patch for newer bcrypt versions
from app.utils.passlib_patch import apply_patch as apply_passlib_patch
apply_passlib_patch()

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

# Use the same database URL as production but add a test schema prefix
# Parse the database URL to handle SSL properly
url = urlparse(settings.DATABASE_URL)
query_params = parse_qs(url.query)

# Remove sslmode from the URL and handle it in connect_args
ssl_mode = query_params.pop('sslmode', ['prefer'])[0]
cleaned_url = f"{url.scheme}://{url.netloc}{url.path}"
if query_params:
    cleaned_url += '?' + '&'.join(f"{k}={v[0]}" for k, v in query_params.items())

# Create test engine and session with proper SSL configuration
TEST_DATABASE_URL = cleaned_url.replace("postgres://", "postgresql+asyncpg://")

# Create test engine and session
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,  # Set to True for debugging
    future=True,
    poolclass=NullPool,
    connect_args={
        "ssl": ssl_mode == "require"
    }
)
TestingSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Test upload directory
TEST_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "test_uploads")
TEST_ASSIGNMENT_DIR = os.path.join(TEST_UPLOAD_DIR, "assignments")

# Override the get_db dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Test client
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client():
    # Use AsyncClient for async tests
    async with AsyncClient(base_url="http://testserver") as ac:
        yield ac

# Setup and teardown for each test
@pytest.fixture(autouse=True)
async def setup_db():
    # Create a unique test schema name for this test run to isolate test data
    test_schema = f"test_{uuid.uuid4().hex[:8]}"
    
    # Create test schema and tables within that schema
    async with engine.begin() as conn:
        # Create the test schema
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {test_schema}"))
        
        # Set the search path to use our test schema
        await conn.execute(text(f"SET search_path TO {test_schema}"))
        
        # Create all tables in the test schema
        await conn.run_sync(Base.metadata.create_all)
        
        # Verify that tables were created
        tables = await conn.run_sync(lambda sync_conn: sync_conn.dialect.get_table_names(sync_conn, schema=test_schema))
        print(f"Created tables in schema {test_schema}: {tables}")
        
        if not tables:
            print(f"WARNING: No tables were created in schema {test_schema}!")
    
    # Create test upload directories
    if not os.path.exists(TEST_UPLOAD_DIR):
        os.makedirs(TEST_UPLOAD_DIR)
    if not os.path.exists(TEST_ASSIGNMENT_DIR):
        os.makedirs(TEST_ASSIGNMENT_DIR)
    
    # Set the schema for all database operations in this test session
    @event.listens_for(engine.sync_engine, "connect")
    def set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET search_path TO {test_schema}")
        cursor.close()
    
    yield
    
    # Clean up: drop the test schema
    async with engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {test_schema} CASCADE"))
    
    # Close all connections
    await engine.dispose()
    
    # Remove test upload directories
    if os.path.exists(TEST_UPLOAD_DIR):
        print("Cleaning up test uploads...")
        shutil.rmtree(TEST_UPLOAD_DIR)

# Fixture for database session
@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

# Fixture for test users
@pytest.fixture
async def test_users(db_session):
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
    
    db_session.add(faculty_user)
    db_session.add(student_user)
    await db_session.commit()
    
    return {
        "faculty": faculty_user,
        "student": student_user
    }

# Fixture for JWT tokens
@pytest.fixture
async def tokens(test_users):
    faculty_token = create_access_token({
        "email": "faculty@test.com",
        "role": "faculty",
        "sub": str(test_users["faculty"].id)
    })
    
    student_token = create_access_token({
        "email": "student@test.com",
        "role": "student",
        "sub": str(test_users["student"].id)
    })
    
    return {
        "faculty": faculty_token,
        "student": student_token
    }

# Fixture for test assignment
@pytest.fixture
async def test_assignment(db_session, test_users):
    assignment = Assignment(
        id=uuid.uuid4(),
        title="Test Assignment",
        description="This is a test assignment",
        course_id=uuid.uuid4(),
        created_by=test_users["faculty"].id,
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
    submission = Submission(
        id=uuid.uuid4(),
        assignment_id=test_assignment.id,
        student_id=test_users["student"].id,
        submitted_at=datetime.now(UTC),
        status="submitted",
        content="This is a test submission content",
        file_name="test_file.txt",
        file_size=1024,
        file_type="text/plain"
    )
    
    db_session.add(submission)
    await db_session.commit()
    await db_session.refresh(submission)
    
    return submission 