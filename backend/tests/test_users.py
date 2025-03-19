import pytest
from httpx import AsyncClient
# from app.main import app
from app.database import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import bcrypt
import uuid

@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def setup_test_data(async_session: AsyncSession):
    # Create test users
    hashed_password = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
    users = [
        User(id=uuid.uuid4(), email="student@example.com", name="Student User", role="student", hashed_password=hashed_password),
        User(id=uuid.uuid4(), email="faculty@example.com", name="Faculty User", role="faculty", hashed_password=hashed_password),
        User(id=uuid.uuid4(), email="support@example.com", name="Support User", role="support", hashed_password=hashed_password),
    ]
    async_session.add_all(users)
    await async_session.commit()
    return users

@pytest.mark.asyncio
async def test_get_all_users(test_client, setup_test_data, mocker):
    # Mock authentication and role
    mocker.patch('app.services.auth_service.get_current_user', return_value={'role': 'support'})
    
    response = await test_client.get('/users')
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

@pytest.mark.asyncio
async def test_get_user_profile(test_client, setup_test_data, mocker):
    user = setup_test_data[0]
    mocker.patch('app.services.auth_service.require_auth', return_value={
        'id': str(user.id),
        'email': user.email,
        'name': user.name,
        'role': user.role
    })
    response = await test_client.get('/user/profile')
    assert response.status_code == 200
    assert response.json()["email"] == user.email

@pytest.mark.asyncio
async def test_update_user_profile(test_client, setup_test_data, mocker):
    user = setup_test_data[0]
    mocker.patch('app.services.auth_service.require_auth', return_value={
        'id': str(user.id),
        'email': user.email,
        'name': user.name,
        'role': user.role
    })
    update_data = {"name": "Updated Name"}
    response = await test_client.put('/user/profile', json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_fetch_user_courses(test_client, setup_test_data, mocker):
    user = setup_test_data[0]
    mocker.patch('app.services.auth_service.get_current_user', return_value={'id': str(user.id), 'email': user.email, 'role': 'student'})
    mocker.patch('app.services.user_service.get_all_user_courses', return_value=[{"id": "course123", "name": "Test Course"}])

    response = await test_client.get('/user/courses')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Course"

@pytest.mark.asyncio
async def test_get_user_not_found(test_client, mocker):
    mocker.patch('app.services.auth_service.require_auth', return_value={'id': str(uuid.uuid4()), 'email': 'fake@example.com', 'role': 'student'})
    response = await test_client.get('/user/profile')
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"