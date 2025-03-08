import pytest
import uuid
import json
from datetime import datetime, timedelta, UTC
from fastapi import status
from httpx import AsyncClient

# Test create assignment endpoint
@pytest.mark.asyncio
async def test_create_assignment_endpoint(async_client, tokens, test_users):
    # Prepare test data
    assignment_data = {
        "title": "API Test Assignment",
        "description": "This is a test assignment created via API",
        "course_id": str(uuid.uuid4()),
        "due_date": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
        "points": 100,
        "status": "draft",
        "submission_type": "file",
        "allow_late_submissions": True,
        "late_penalty": 10,
        "plagiarism_detection": True,
        "file_types": "pdf,doc,docx,txt",
        "max_file_size": 10
    }
    
    # Test with faculty token (should succeed)
    response = await async_client.post(
        "/api/v1/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == assignment_data["title"]
    assert data["description"] == assignment_data["description"]
    
    # Test with student token (should fail)
    response = await async_client.post(
        "/api/v1/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Test get assignments endpoint
@pytest.mark.asyncio
async def test_get_assignments_endpoint(async_client, tokens, test_assignment):
    # Test with valid course_id
    response = await async_client.get(
        f"/api/v1/assignments?course_id={test_assignment.course_id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(a["id"] == str(test_assignment.id) for a in data)
    
    # Test with invalid course_id
    response = await async_client.get(
        f"/api/v1/assignments?course_id={uuid.uuid4()}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

# Test get assignment details endpoint
@pytest.mark.asyncio
async def test_get_assignment_details_endpoint(async_client, tokens, test_assignment):
    # Test with valid assignment_id
    response = await async_client.get(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_assignment.id)
    assert data["title"] == test_assignment.title
    assert data["description"] == test_assignment.description
    
    # Test with invalid assignment_id
    response = await async_client.get(
        f"/api/v1/assignments/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test update assignment endpoint
@pytest.mark.asyncio
async def test_update_assignment_endpoint(async_client, tokens, test_assignment):
    # Prepare update data
    update_data = {
        "title": "Updated API Assignment",
        "description": "This assignment was updated via API",
        "points": 150
    }
    
    # Test with faculty token (should succeed)
    response = await async_client.put(
        f"/api/v1/assignments/{test_assignment.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_assignment.id)
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["points"] == update_data["points"]
    
    # Test with student token (should fail)
    response = await async_client.put(
        f"/api/v1/assignments/{test_assignment.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Test delete assignment endpoint
@pytest.mark.asyncio
async def test_delete_assignment_endpoint(async_client, tokens, test_assignment):
    # Test with student token (should fail)
    response = await async_client.delete(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test with faculty token (should succeed)
    response = await async_client.delete(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Assignment deleted successfully"
    
    # Verify assignment is deleted
    response = await async_client.get(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test submit assignment endpoint
@pytest.mark.asyncio
async def test_submit_assignment_endpoint(async_client, tokens, test_assignment):
    # Prepare submission data
    submission_data = {
        "content": "This is a test submission content via API",
        "status": "submitted"
    }
    
    # Test with student token (should succeed)
    response = await async_client.post(
        f"/api/v1/assignments/{test_assignment.id}/submit",
        data=submission_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Assignment submitted successfully"
    assert data["submission_id"] is not None
    
    # Test submitting again (should update existing submission)
    updated_submission_data = {
        "content": "This is an updated submission content",
        "status": "submitted"
    }
    
    response = await async_client.post(
        f"/api/v1/assignments/{test_assignment.id}/submit",
        data=updated_submission_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Assignment submitted successfully"
    assert data["submission_id"] is not None

# Test get my submission endpoint
@pytest.mark.asyncio
async def test_get_my_submission_endpoint(async_client, tokens, test_assignment, test_submission):
    # Test with student token (should succeed)
    response = await async_client.get(
        f"/api/v1/assignments/{test_assignment.id}/my-submission",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Submission retrieved successfully"
    assert data["submission"] is not None
    assert data["submission"]["id"] == str(test_submission.id)
    assert data["submission"]["assignment_id"] == str(test_assignment.id)
    assert data["submission"]["student_id"] == str(test_submission.student_id)
    
    # Test with faculty token (should return null submission)
    response = await async_client.get(
        f"/api/v1/assignments/{test_assignment.id}/my-submission",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Submission retrieved successfully"
    assert data["submission"] is None

# Test get all submissions endpoint
@pytest.mark.asyncio
async def test_get_all_submissions_endpoint(async_client, tokens, test_assignment, test_submission):
    # Test with faculty token (should succeed)
    response = await async_client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(s["id"] == str(test_submission.id) for s in data)
    
    # Test with student token (should fail)
    response = await async_client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Test grade submission endpoint
@pytest.mark.asyncio
async def test_grade_submission_endpoint(async_client, tokens, test_assignment, test_submission):
    # Prepare grade data
    grade_data = {
        "grade": 85,
        "feedback": "Good work, but could improve code organization"
    }
    
    # Test with student token (should fail)
    response = await async_client.put(
        f"/api/v1/assignments/{test_assignment.id}/grade/{test_submission.id}",
        json=grade_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test with faculty token (should succeed)
    response = await async_client.put(
        f"/api/v1/assignments/{test_assignment.id}/grade/{test_submission.id}",
        json=grade_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Submission graded successfully"
    assert data["submission_id"] == str(test_submission.id)
    assert data["grade"] == grade_data["grade"]

# Test plagiarism report endpoint
@pytest.mark.asyncio
async def test_plagiarism_report_endpoint(async_client, tokens, test_assignment, test_submission):
    # Test with student token (should fail)
    response = await async_client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{test_submission.id}/plagiarism",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test with faculty token (should succeed)
    response = await async_client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{test_submission.id}/plagiarism",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Plagiarism report retrieved successfully"
    assert "plagiarism_score" in data
    assert "report" in data 