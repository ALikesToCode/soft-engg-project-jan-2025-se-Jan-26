import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.models.user import User
from app.utils.jwt_utils import create_access_token
from main import app

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

# Test endpoint
@pytest.mark.asyncio
async def test_academic_integrity_test_endpoint(client):
    """Test the academic integrity test endpoint"""
    response = client.get("/api/v1/academic-integrity/test")
    assert response.status_code == status.HTTP_200_OK

# Flag tests
@pytest.mark.asyncio
@patch('app.routes.academic_integrity.get_flagged_interactions')
async def test_get_flagged_interactions(mock_get_flags, client, faculty_token):
    """Test getting flagged interactions"""
    # Mock the flags response
    mock_get_flags.return_value = [
        {
            "id": "flag_1",
            "content": "Suspicious content 1",
            "context": {"assignment_id": "123", "submission_id": "456"},
            "source": "submission",
            "severity": "high",
            "status": "pending",
            "course_id": "course_1",
            "user_id": "user_1",
            "created_at": "2024-03-05T12:00:00Z",
            "updated_at": "2024-03-05T12:00:00Z",
            "comments": []
        },
        {
            "id": "flag_2",
            "content": "Suspicious content 2",
            "context": {"assignment_id": "789", "submission_id": "012"},
            "source": "chat",
            "severity": "medium",
            "status": "reviewed",
            "course_id": "course_2",
            "user_id": "user_2",
            "created_at": "2024-03-04T12:00:00Z",
            "updated_at": "2024-03-05T10:00:00Z",
            "reviewed_by": "faculty_1",
            "comments": [{"text": "Reviewing this flag", "user_id": "faculty_1"}]
        }
    ]
    
    # Send request with filters
    response = client.get(
        "/api/v1/academic-integrity/flags?status=pending&severity=high&source=submission&course_id=course_1",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == "flag_1"
    assert data[0]["severity"] == "high"
    assert data[1]["id"] == "flag_2"
    assert data[1]["severity"] == "medium"

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.update_flag_status')
async def test_update_flag_status(mock_update, client, faculty_token):
    """Test updating flag status"""
    # Mock the update response
    mock_update.return_value = {
        "id": "flag_1",
        "content": "Suspicious content 1",
        "context": {"assignment_id": "123", "submission_id": "456"},
        "source": "submission",
        "severity": "high",
        "status": "reviewed",
        "course_id": "course_1",
        "user_id": "user_1",
        "created_at": "2024-03-05T12:00:00Z",
        "updated_at": "2024-03-06T12:00:00Z",
        "reviewed_by": "faculty_1",
        "comments": [{"text": "This has been reviewed", "user_id": "faculty_1"}]
    }
    
    # Update data
    update_data = {
        "status": "reviewed",
        "comment": "This has been reviewed"
    }
    
    # Send request
    response = client.put(
        "/api/v1/academic-integrity/flags/flag_1",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json=update_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "flag_1"
    assert data["status"] == "reviewed"
    assert data["reviewed_by"] == "faculty_1"
    assert len(data["comments"]) == 1
    assert data["comments"][0]["text"] == "This has been reviewed"

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.escalate_flag')
async def test_escalate_flag(mock_escalate, client, faculty_token):
    """Test escalating a flag"""
    # Mock the escalation response
    mock_escalate.return_value = {
        "id": "flag_1",
        "content": "Suspicious content 1",
        "context": {"assignment_id": "123", "submission_id": "456"},
        "source": "submission",
        "severity": "high",
        "status": "escalated",
        "course_id": "course_1",
        "user_id": "user_1",
        "created_at": "2024-03-05T12:00:00Z",
        "updated_at": "2024-03-06T12:00:00Z",
        "reviewed_by": "faculty_1",
        "escalated_to": ["support_1", "admin_1"],
        "comments": [
            {"text": "This has been reviewed", "user_id": "faculty_1"},
            {"text": "Escalating to support team", "user_id": "faculty_1"}
        ]
    }
    
    # Escalation data
    escalation_data = {
        "reason": "Serious academic integrity concern",
        "escalate_to": ["support_1", "admin_1"],
        "priority": "high",
        "additional_notes": "Please review this case urgently"
    }
    
    # Send request
    response = client.post(
        "/api/v1/academic-integrity/flags/flag_1/escalate",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json=escalation_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "flag_1"
    assert data["status"] == "escalated"
    assert "escalated_to" in data
    assert len(data["escalated_to"]) == 2
    assert "support_1" in data["escalated_to"]
    assert "admin_1" in data["escalated_to"]

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.get_flag_statistics')
async def test_get_flag_statistics(mock_stats, client, faculty_token):
    """Test getting flag statistics"""
    # Mock the statistics response
    mock_stats.return_value = {
        "total_flags": 25,
        "by_status": {
            "pending": 10,
            "reviewed": 8,
            "escalated": 5,
            "resolved": 2
        },
        "by_severity": {
            "low": 5,
            "medium": 12,
            "high": 8
        },
        "by_source": {
            "submission": 15,
            "chat": 8,
            "other": 2
        },
        "recent_flags": [
            {
                "id": "flag_1",
                "content": "Suspicious content 1",
                "source": "submission",
                "severity": "high",
                "status": "pending",
                "created_at": "2024-03-05T12:00:00Z"
            }
        ],
        "course_id": "course_1"
    }
    
    # Send request
    response = client.get(
        "/api/v1/academic-integrity/statistics/course_1",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_flags"] == 25
    assert "by_status" in data
    assert "by_severity" in data
    assert "by_source" in data
    assert data["by_status"]["pending"] == 10
    assert data["by_severity"]["high"] == 8
    assert data["by_source"]["submission"] == 15
    assert len(data["recent_flags"]) == 1

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.get_flag_audit_trail')
async def test_get_flag_audit_trail(mock_audit, client, faculty_token):
    """Test getting flag audit trail"""
    # Mock the audit trail response
    mock_audit.return_value = [
        {
            "id": "audit_1",
            "flag_id": "flag_1",
            "action": "create",
            "user_id": "system",
            "timestamp": "2024-03-05T12:00:00Z",
            "details": {"reason": "Automated detection"}
        },
        {
            "id": "audit_2",
            "flag_id": "flag_1",
            "action": "update",
            "user_id": "faculty_1",
            "timestamp": "2024-03-06T10:00:00Z",
            "details": {"status": {"from": "pending", "to": "reviewed"}}
        },
        {
            "id": "audit_3",
            "flag_id": "flag_1",
            "action": "escalate",
            "user_id": "faculty_1",
            "timestamp": "2024-03-06T11:00:00Z",
            "details": {"escalated_to": ["support_1", "admin_1"]}
        }
    ]
    
    # Send request
    response = client.get(
        "/api/v1/academic-integrity/flags/flag_1/audit",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["action"] == "create"
    assert data[1]["action"] == "update"
    assert data[2]["action"] == "escalate"
    assert data[0]["timestamp"] == "2024-03-05T12:00:00Z"
    assert data[1]["user_id"] == "faculty_1"

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.validate_llm_request')
async def test_validate_llm_request(mock_validate, client, faculty_token):
    """Test validating LLM request"""
    # Mock the validation response
    mock_validate.return_value = {
        "is_valid": True,
        "confidence": 0.95,
        "flags": [],
        "message": "Request appears to be valid"
    }
    
    # Validation data
    validation_data = {
        "content": "What is the capital of France?"
    }
    
    # Send request
    response = client.post(
        "/api/v1/academic-integrity/validate-llm-request",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json=validation_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_valid"] is True
    assert data["confidence"] == 0.95
    assert len(data["flags"]) == 0
    assert data["message"] == "Request appears to be valid"

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.flag_submission')
async def test_flag_submission(mock_flag, client, faculty_token):
    """Test flagging a submission"""
    assignment_id = str(uuid.uuid4())
    submission_id = str(uuid.uuid4())
    
    # Mock the flag response
    mock_flag.return_value = {
        "message": "Submission flagged successfully",
        "flag_id": "flag_1"
    }
    
    # Flag data
    flag_data = {
        "reason": "Suspected plagiarism",
        "status": "pending"
    }
    
    # Send request
    response = client.post(
        f"/api/v1/academic-integrity/assignments/{assignment_id}/submissions/{submission_id}/flag",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json=flag_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Submission flagged successfully"
    assert data["flag_id"] == "flag_1"

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.get_submission_flag')
async def test_get_submission_flag(mock_get_flag, client, faculty_token):
    """Test getting a submission flag"""
    assignment_id = str(uuid.uuid4())
    submission_id = str(uuid.uuid4())
    
    # Mock the flag response
    mock_get_flag.return_value = {
        "id": "flag_1",
        "reason": "Suspected plagiarism",
        "status": "pending",
        "created_at": "2024-03-05T12:00:00Z",
        "created_by": "faculty_1",
        "assignment_id": assignment_id,
        "submission_id": submission_id
    }
    
    # Send request
    response = client.get(
        f"/api/v1/academic-integrity/assignments/{assignment_id}/submissions/{submission_id}/flag",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "flag_1"
    assert data["reason"] == "Suspected plagiarism"
    assert data["status"] == "pending"
    assert data["assignment_id"] == assignment_id
    assert data["submission_id"] == submission_id

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.update_submission_flag')
async def test_update_submission_flag(mock_update, client, faculty_token):
    """Test updating a submission flag"""
    assignment_id = str(uuid.uuid4())
    submission_id = str(uuid.uuid4())
    
    # Mock the update response
    mock_update.return_value = {
        "message": "Flag updated successfully",
        "flag": {
            "id": "flag_1",
            "reason": "Confirmed plagiarism",
            "status": "resolved",
            "resolution_notes": "Student admitted to plagiarism",
            "created_at": "2024-03-05T12:00:00Z",
            "updated_at": "2024-03-06T12:00:00Z",
            "created_by": "faculty_1",
            "assignment_id": assignment_id,
            "submission_id": submission_id
        }
    }
    
    # Update data
    update_data = {
        "reason": "Confirmed plagiarism",
        "status": "resolved",
        "resolution_notes": "Student admitted to plagiarism"
    }
    
    # Send request
    response = client.put(
        f"/api/v1/academic-integrity/assignments/{assignment_id}/submissions/{submission_id}/flag",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json=update_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Flag updated successfully"
    assert data["flag"]["id"] == "flag_1"
    assert data["flag"]["reason"] == "Confirmed plagiarism"
    assert data["flag"]["status"] == "resolved"
    assert data["flag"]["resolution_notes"] == "Student admitted to plagiarism"

@pytest.mark.asyncio
@patch('app.routes.academic_integrity.get_all_flags')
async def test_get_all_flags(mock_get_all, client, faculty_token):
    """Test getting all flags"""
    # Mock the flags response
    mock_get_all.return_value = [
        {
            "id": "flag_1",
            "reason": "Suspected plagiarism",
            "status": "pending",
            "created_at": "2024-03-05T12:00:00Z",
            "created_by": "faculty_1",
            "assignment_id": str(uuid.uuid4()),
            "submission_id": str(uuid.uuid4())
        },
        {
            "id": "flag_2",
            "reason": "Confirmed plagiarism",
            "status": "resolved",
            "resolution_notes": "Student admitted to plagiarism",
            "created_at": "2024-03-04T12:00:00Z",
            "updated_at": "2024-03-05T12:00:00Z",
            "created_by": "faculty_1",
            "assignment_id": str(uuid.uuid4()),
            "submission_id": str(uuid.uuid4())
        }
    ]
    
    # Send request with status filter
    response = client.get(
        "/api/v1/academic-integrity/flags?status=pending",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == "flag_1"
    assert data[0]["status"] == "pending"
    assert data[1]["id"] == "flag_2"
    assert data[1]["status"] == "resolved" 