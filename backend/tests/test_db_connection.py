import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
import uuid

@pytest.mark.asyncio
async def test_db_connection(db_session):
    """Test that we can connect to the database and perform basic operations."""
    # Get the actual session from the async generator
    session = None
    if hasattr(db_session, "__aiter__"):  # Check if it's an async generator
        async for s in db_session:
            session = s
            break
    else:  # If it's already a session
        session = db_session
    
    if not session:
        pytest.fail("Could not get session from db_session fixture")
    
    # Create a test user
    test_user = User(
        id=uuid.uuid4(),
        email="test_db_connection@example.com",
        name="Test DB Connection",
        hashed_password="test_password",
        is_google_user=False,
        role="student"
    )
    
    # Add the user to the session
    session.add(test_user)
    
    # Commit the changes
    await session.commit()
    
    # Refresh the user from the database
    await session.refresh(test_user)
    
    # Verify the user was created
    assert test_user.id is not None
    assert test_user.email == "test_db_connection@example.com"
    
    # Clean up
    await session.delete(test_user)
    await session.commit() 