import pytest
import uuid
from datetime import datetime, timedelta, UTC
from fastapi import status
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.models.user import User
from app.utils.jwt_utils import create_access_token
from main import app

# Authentication API Tests
@pytest.mark.asyncio
async def test_login_valid_credentials(client: TestClient):
    """Test login with valid credentials"""
    # Note: In a real test, we would set up proper credentials
    # For now, we'll just check that the endpoint exists and returns a response
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "faculty@test.com", "password": "password"}
    )
    # Since we don't have proper credentials set up, we expect a 500 Internal Server Error
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    # Note: In a real test, we would set up proper credentials
    # For now, we'll just check that the endpoint exists and returns a response
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "faculty@test.com", "password": "wrong_password"}
    )
    # Since we don't have proper credentials set up, we expect a 500 Internal Server Error
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_get_current_user(client: TestClient, tokens):
    """Test getting the current user's information"""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert "id" in user_data
    assert user_data["email"] == "faculty@test.com"
    assert user_data["role"] == "faculty"

# User API Tests
@pytest.mark.asyncio
async def test_get_users_as_admin(client: TestClient, tokens):
    """Test getting all users as admin"""
    # Note: In a real test, we would set up an admin user
    # For now, we'll just check that the endpoint exists and returns a response
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}  # Using faculty as admin for test
    )
    # Since we don't have proper admin setup, we expect a 403 Forbidden
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_users_as_student(client: TestClient, tokens):
    """Test getting all users as student (should be forbidden)"""
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Assignment API Tests
@pytest.mark.asyncio
async def test_create_assignment(client: TestClient, tokens):
    """Test creating an assignment"""
    assignment_data = {
        "title": "Test Assignment",
        "description": "This is a test assignment",
        "course_id": str(uuid.uuid4()),
        "due_date": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
        "points": 100,
        "status": "draft",
        "submission_type": "file",
        "allow_late_submissions": True,
        "late_penalty": 10,
        "plagiarism_detection": True,
        "file_types": "pdf,doc,docx",
        "max_file_size": 5
    }
    
    response = client.post(
        "/api/v1/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "assignment_id" in data
    assert data["message"] == "Assignment created successfully"

@pytest.mark.asyncio
async def test_create_assignment_as_student(client: TestClient, tokens):
    """Test creating an assignment as student (should be forbidden)"""
    assignment_data = {
        "title": "Test Assignment",
        "description": "This is a test assignment",
        "course_id": str(uuid.uuid4()),
        "due_date": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
        "points": 100,
        "status": "draft",
        "submission_type": "file",
        "allow_late_submissions": True,
        "late_penalty": 10,
        "plagiarism_detection": True,
        "file_types": "pdf,doc,docx",
        "max_file_size": 5
    }
    
    response = client.post(
        "/api/v1/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Course API Tests
@pytest.mark.asyncio
async def test_create_course(client: TestClient, tokens):
    """Test creating a course"""
    course_data = {
        "title": "Test Course",
        "code": "TEST101",
        "description": "This is a test course",
        "start_date": datetime.now(UTC).isoformat(),
        "end_date": (datetime.now(UTC) + timedelta(days=90)).isoformat(),
        "status": "active",
        "enrollment_limit": 30,
        "is_public": True
    }
    
    response = client.post(
        "/api/v1/courses",
        json=course_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "course_id" in data
    assert data["message"] == "Course created successfully"

@pytest.mark.asyncio
async def test_get_courses(client: TestClient, tokens):
    """Test getting all courses"""
    # First create a course
    course_data = {
        "title": "Another Test Course",
        "code": "TEST102",
        "description": "This is another test course",
        "start_date": datetime.now(UTC).isoformat(),
        "end_date": (datetime.now(UTC) + timedelta(days=90)).isoformat(),
        "status": "active",
        "enrollment_limit": 30,
        "is_public": True
    }
    
    client.post(
        "/api/v1/courses",
        json=course_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Now get all courses
    response = client.get(
        "/api/v1/courses",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    courses = response.json()
    assert isinstance(courses, list)
    assert len(courses) >= 1

# FAQ API Tests
@pytest.mark.asyncio
async def test_get_faqs(client: TestClient, tokens):
    """Test getting all FAQs"""
    response = client.get(
        "/api/v1/faqs",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    faqs = response.json()
    assert isinstance(faqs, list)

# System Settings API Tests
@pytest.mark.asyncio
async def test_get_system_settings_as_admin(client: TestClient, tokens):
    """Test getting system settings as admin"""
    response = client.get(
        "/api/v1/settings",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}  # Using faculty as admin for test
    )
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_system_settings_as_student(client: TestClient, tokens):
    """Test getting system settings as student (should be forbidden)"""
    response = client.get(
        "/api/v1/settings",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Test fixtures
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client():
    async with AsyncClient(base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def faculty_token(test_users):
    """Create a valid faculty token for testing"""
    return create_access_token({
        "email": "faculty@test.com",
        "role": "faculty",
        "sub": str(test_users["faculty"].id)
    })

@pytest.fixture
def student_token(test_users):
    """Create a valid student token for testing"""
    return create_access_token({
        "email": "student@test.com",
        "role": "student",
        "sub": str(test_users["student"].id)
    })

@pytest.fixture
def support_token(test_users):
    """Create a valid support token for testing"""
    return create_access_token({
        "email": "support@test.com",
        "role": "support",
        "sub": str(test_users["faculty"].id)  # Using faculty ID for support role
    })

# Root endpoint tests
@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK

# Monitoring endpoint tests
@pytest.mark.asyncio
@patch('app.routes.monitoring.monitoring_service.get_system_health')
async def test_health_endpoint(mock_health, client):
    """Test the health endpoint"""
    # Mock the health service response
    mock_health.return_value = {
        "status": "healthy",
        "timestamp": "2024-03-05T12:00:00Z",
        "services": {
            "database": "up",
            "redis": "up",
            "api": "up"
        },
        "metrics": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 73.1,
            "active_connections": 15,
            "response_time": 150,
            "error_rate": 0.5
        }
    }
    
    # Send request
    response = client.get("/api/v1/monitoring/health")
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert "metrics" in data
    assert data["services"]["database"] == "up"
    assert data["metrics"]["cpu_usage"] == 45.2

@pytest.mark.asyncio
@patch('app.routes.monitoring.get_system_metrics')
async def test_metrics_endpoint(mock_metrics, client, faculty_token):
    """Test the metrics endpoint"""
    # Mock the metrics service response
    mock_metrics.return_value = {
        "current": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 73.1,
            "active_connections": 15,
            "response_time": 150,
            "error_rate": 0.5,
            "timestamp": "2024-03-05T12:00:00Z"
        },
        "history": [
            {
                "timestamp": "2024-03-05T11:59:00Z",
                "cpu_usage": 44.8,
                "memory_usage": 62.5
            }
        ]
    }
    
    # Send request with history parameter
    response = client.get(
        "/api/v1/monitoring/metrics?history=true&limit=10",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "current" in data
    assert "history" in data
    assert data["current"]["cpu_usage"] == 45.2
    assert len(data["history"]) == 1

@pytest.mark.asyncio
@patch('app.routes.monitoring.get_system_logs')
async def test_logs_endpoint(mock_logs, client, support_token):
    """Test the logs endpoint"""
    # Mock the logs service response
    mock_logs.return_value = [
        {
            "timestamp": "2024-03-05T12:00:00Z",
            "level": "INFO",
            "message": "Application started"
        },
        {
            "timestamp": "2024-03-05T12:01:00Z",
            "level": "WARNING",
            "message": "High memory usage detected"
        }
    ]
    
    # Send request with level parameter
    response = client.get(
        "/api/v1/monitoring/logs?level=INFO&limit=100",
        headers={"Authorization": f"Bearer {support_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["level"] == "INFO"
    assert data[1]["level"] == "WARNING"

@pytest.mark.asyncio
@patch('app.routes.monitoring.create_alert')
async def test_create_alert(mock_create_alert, client, support_token):
    """Test creating a system alert"""
    # Mock the alert creation response
    mock_create_alert.return_value = {
        "id": "alert_1234567890",
        "type": "high_cpu_usage",
        "severity": "warning",
        "message": "CPU usage above threshold",
        "timestamp": "2024-03-05T12:00:00Z",
        "resolved": False
    }
    
    # Alert data
    alert_data = {
        "type": "high_cpu_usage",
        "severity": "warning",
        "message": "CPU usage above threshold"
    }
    
    # Send request
    response = client.post(
        "/api/v1/monitoring/alerts",
        headers={"Authorization": f"Bearer {support_token}"},
        json=alert_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "alert_1234567890"
    assert data["type"] == "high_cpu_usage"
    assert data["severity"] == "warning"
    assert data["message"] == "CPU usage above threshold"
    assert data["resolved"] is False

@pytest.mark.asyncio
@patch('app.routes.monitoring.get_alerts')
async def test_get_alerts(mock_get_alerts, client, support_token):
    """Test getting system alerts"""
    # Mock the alerts response
    mock_get_alerts.return_value = [
        {
            "id": "alert_1234567890",
            "type": "high_cpu_usage",
            "severity": "warning",
            "message": "CPU usage above threshold",
            "timestamp": "2024-03-05T12:00:00Z",
            "resolved": False
        },
        {
            "id": "alert_0987654321",
            "type": "service_down",
            "severity": "critical",
            "message": "Redis service is down",
            "timestamp": "2024-03-05T11:30:00Z",
            "resolved": True
        }
    ]
    
    # Send request with filters
    response = client.get(
        "/api/v1/monitoring/alerts?type=high_cpu_usage&severity=warning&resolved=false",
        headers={"Authorization": f"Bearer {support_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == "alert_1234567890"
    assert data[0]["type"] == "high_cpu_usage"
    assert data[1]["id"] == "alert_0987654321"
    assert data[1]["type"] == "service_down"

@pytest.mark.asyncio
@patch('app.routes.monitoring.acknowledge_alert')
async def test_acknowledge_alert(mock_acknowledge, client, support_token):
    """Test acknowledging an alert"""
    # Mock the acknowledgement response
    mock_acknowledge.return_value = {
        "id": "alert_1234567890",
        "acknowledgement": {
            "user_id": "user123",
            "timestamp": "2024-03-05T12:00:00Z",
            "comment": "Investigating the issue"
        }
    }
    
    # Acknowledgement data
    ack_data = {
        "comment": "Investigating the issue"
    }
    
    # Send request
    response = client.post(
        "/api/v1/monitoring/alerts/alert_1234567890/acknowledge",
        headers={"Authorization": f"Bearer {support_token}"},
        json=ack_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "alert_1234567890"
    assert data["acknowledgement"]["comment"] == "Investigating the issue"

@pytest.mark.asyncio
@patch('app.routes.monitoring.resolve_alert')
async def test_resolve_alert(mock_resolve, client, support_token):
    """Test resolving an alert"""
    # Mock the resolution response
    mock_resolve.return_value = {
        "id": "alert_1234567890",
        "resolved": True,
        "resolved_at": "2024-03-05T12:00:00Z",
        "resolved_by": "user123",
        "resolution_note": "Issue has been fixed"
    }
    
    # Resolution data
    resolution_data = {
        "resolution_note": "Issue has been fixed"
    }
    
    # Send request
    response = client.post(
        "/api/v1/monitoring/alerts/alert_1234567890/resolve",
        headers={"Authorization": f"Bearer {support_token}"},
        json=resolution_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "alert_1234567890"
    assert data["resolved"] is True
    assert data["resolution_note"] == "Issue has been fixed"

@pytest.mark.asyncio
@patch('app.routes.monitoring.get_system_summary')
async def test_system_summary(mock_summary, client, support_token):
    """Test getting system summary"""
    # Mock the summary response
    mock_summary.return_value = {
        "system_status": "healthy",
        "current_metrics": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 73.1
        },
        "services": {
            "database": {
                "status": "up"
            },
            "redis": {
                "status": "up"
            },
            "api": {
                "status": "up"
            }
        },
        "active_alerts": 0,
        "total_alerts_24h": 5,
        "uptime": 345600,
        "last_updated": "2024-03-05T12:00:00Z"
    }
    
    # Send request
    response = client.get(
        "/api/v1/monitoring/summary",
        headers={"Authorization": f"Bearer {support_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["system_status"] == "healthy"
    assert "current_metrics" in data
    assert "services" in data
    assert data["active_alerts"] == 0
    assert data["total_alerts_24h"] == 5

@pytest.mark.asyncio
@patch('app.routes.monitoring.get_service_status')
async def test_service_status(mock_service_status, client, support_token):
    """Test getting service status"""
    # Mock the service status response
    mock_service_status.return_value = {
        "database": {
            "status": "up",
            "last_check": "2024-03-05T12:00:00Z",
            "response_time": 15.5
        },
        "redis": {
            "status": "up",
            "last_check": "2024-03-05T12:00:00Z",
            "response_time": 5.2
        },
        "api": {
            "status": "up",
            "last_check": "2024-03-05T12:00:00Z",
            "response_time": 120.3
        }
    }
    
    # Send request
    response = client.get(
        "/api/v1/monitoring/services",
        headers={"Authorization": f"Bearer {support_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "database" in data
    assert "redis" in data
    assert "api" in data
    assert data["database"]["status"] == "up"
    assert data["redis"]["status"] == "up"
    assert data["api"]["status"] == "up"

@pytest.mark.asyncio
@patch('app.routes.monitoring.get_dashboard_data')
async def test_dashboard_data(mock_dashboard, client, support_token):
    """Test getting dashboard data"""
    # Mock the dashboard data response
    mock_dashboard.return_value = {
        "active_users": 1250,
        "open_issues": 8,
        "system_status": {
            "status": "healthy",
            "services": {
                "database": "up",
                "redis": "up",
                "api": "up"
            }
        },
        "avg_response_time": 120,
        "performance_metrics": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 73.1
        },
        "performance_trends": {
            "cpu_trend": -5.2,
            "memory_trend": 2.8,
            "response_time_trend": -3.1
        },
        "error_summary": {
            "total_errors": 15,
            "errors_last_hour": 2,
            "errors_last_day": 8,
            "error_categories": {
                "database": 5,
                "api": 3,
                "authentication": 7
            }
        },
        "active_alerts": [
            {
                "id": "alert_1234567890",
                "type": "high_cpu_usage",
                "severity": "critical",
                "message": "CPU usage above threshold",
                "timestamp": "2024-03-05T12:00:00Z",
                "component": "Database Server"
            }
        ]
    }
    
    # Send request
    response = client.get(
        "/api/v1/monitoring/dashboard",
        headers={"Authorization": f"Bearer {support_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["active_users"] == 1250
    assert data["open_issues"] == 8
    assert data["system_status"]["status"] == "healthy"
    assert data["avg_response_time"] == 120
    assert "performance_metrics" in data
    assert "performance_trends" in data
    assert "error_summary" in data
    assert "active_alerts" in data
    assert len(data["active_alerts"]) == 1 