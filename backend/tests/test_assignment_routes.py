import pytest
import uuid
import json
from datetime import datetime, timedelta, UTC
from fastapi import status
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.utils.jwt_utils import create_access_token

# Test create assignment endpoint
@pytest.mark.asyncio
async def test_create_assignment_endpoint(client: TestClient, tokens, test_users):
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
    response = client.post(
        "/api/v1/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "assignment_id" in data
    
    # Test with student token (should fail)
    response = client.post(
        "/api/v1/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test without token (should fail)
    response = client.post(
        "/api/v1/assignments",
        json=assignment_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test get assignments endpoint
@pytest.mark.asyncio
async def test_get_assignments_endpoint(client: TestClient, tokens, test_assignment):
    # Test with valid course_id
    response = client.get(
        f"/api/v1/assignments?course_id={test_assignment.course_id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assignments = response.json()
    assert isinstance(assignments, list)
    assert len(assignments) >= 1
    
    # Test with invalid course_id
    response = client.get(
        f"/api/v1/assignments?course_id={uuid.uuid4()}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assignments = response.json()
    assert isinstance(assignments, list)
    assert len(assignments) == 0
    
    # Test without course_id
    response = client.get(
        "/api/v1/assignments",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assignments = response.json()
    assert isinstance(assignments, list)

# Test get assignment details endpoint
@pytest.mark.asyncio
async def test_get_assignment_details_endpoint(client: TestClient, tokens, test_assignment):
    # Test with valid assignment_id
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assignment = response.json()
    assert assignment["id"] == str(test_assignment.id)
    assert assignment["title"] == test_assignment.title
    
    # Test with invalid assignment_id
    response = client.get(
        f"/api/v1/assignments/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test update assignment endpoint
@pytest.mark.asyncio
async def test_update_assignment_endpoint(client: TestClient, tokens, test_assignment):
    # Prepare update data
    update_data = {
        "title": "Updated Assignment Title",
        "description": "This assignment has been updated via API",
        "points": 150
    }
    
    # Test with faculty token (should succeed)
    response = client.put(
        f"/api/v1/assignments/{test_assignment.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Assignment updated successfully"
    
    # Verify the update was applied
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    updated_assignment = response.json()
    assert updated_assignment["title"] == update_data["title"]
    assert updated_assignment["description"] == update_data["description"]
    assert updated_assignment["points"] == update_data["points"]
    
    # Test with student token (should fail)
    response = client.put(
        f"/api/v1/assignments/{test_assignment.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Test delete assignment endpoint
@pytest.mark.asyncio
async def test_delete_assignment_endpoint(client: TestClient, tokens, test_assignment):
    # Test with student token (should fail)
    response = client.delete(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test with faculty token (should succeed)
    response = client.delete(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Assignment deleted successfully"
    
    # Verify the assignment was deleted
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test submit assignment endpoint
@pytest.mark.asyncio
async def test_submit_assignment_endpoint(client: TestClient, tokens, test_assignment):
    # Prepare submission data
    submission_data = {
        "content": "This is my submission for the test assignment",
        "status": "submitted"
    }
    
    # Test with student token (should succeed)
    response = client.post(
        f"/api/v1/assignments/{test_assignment.id}/submit",
        data=submission_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "submission_id" in data
    assert data["message"] == "Assignment submitted successfully"
    
    # Test with faculty token (should fail)
    response = client.post(
        f"/api/v1/assignments/{test_assignment.id}/submit",
        data=submission_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test with invalid assignment_id
    response = client.post(
        f"/api/v1/assignments/{uuid.uuid4()}/submit",
        data=submission_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test get my submission endpoint
@pytest.mark.asyncio
async def test_get_my_submission_endpoint(client: TestClient, tokens, test_assignment, test_submission):
    # Test with student token (should succeed)
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/my-submission",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    submission = response.json()
    assert submission["assignment_id"] == str(test_assignment.id)
    assert submission["student_id"] == str(test_submission.student_id)
    
    # Test with faculty token (should fail)
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/my-submission",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Test with invalid assignment_id
    response = client.get(
        f"/api/v1/assignments/{uuid.uuid4()}/my-submission",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test get all submissions endpoint
@pytest.mark.asyncio
async def test_get_all_submissions_endpoint(client: TestClient, tokens, test_assignment, test_submission):
    # Test with faculty token (should succeed)
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    submissions = response.json()
    assert isinstance(submissions, list)
    assert len(submissions) >= 1
    
    # Test with student token (should fail)
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test with invalid assignment_id
    response = client.get(
        f"/api/v1/assignments/{uuid.uuid4()}/submissions",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test grade submission endpoint
@pytest.mark.asyncio
async def test_grade_submission_endpoint(client: TestClient, tokens, test_assignment, test_submission):
    # Prepare grade data
    grade_data = {
        "grade": 95.5,
        "feedback": "Excellent work on this assignment!"
    }
    
    # Test with faculty token (should succeed)
    response = client.put(
        f"/api/v1/assignments/{test_assignment.id}/grade/{test_submission.id}",
        json=grade_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Submission graded successfully"
    
    # Test with student token (should fail)
    response = client.put(
        f"/api/v1/assignments/{test_assignment.id}/grade/{test_submission.id}",
        json=grade_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test with invalid submission_id
    response = client.put(
        f"/api/v1/assignments/{test_assignment.id}/grade/{uuid.uuid4()}",
        json=grade_data,
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test plagiarism report endpoint
@pytest.mark.asyncio
async def test_plagiarism_report_endpoint(client: TestClient, tokens, test_assignment, test_submission):
    # Test with student token (should fail)
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{test_submission.id}/plagiarism",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test with faculty token (should succeed)
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{test_submission.id}/plagiarism",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Test with invalid submission_id
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{uuid.uuid4()}/plagiarism",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test downloading submission file
@pytest.mark.asyncio
async def test_download_submission_file_endpoint(client: TestClient, tokens, test_assignment, test_submission, monkeypatch):
    """Test downloading a submission file"""
    # Setup a mock file path and ensure file_path exists on the test_submission
    from unittest.mock import patch, MagicMock
    import os
    
    # Create a mock file for testing
    test_file_content = b"This is test file content"
    test_file_path = "test_submission_file.pdf"
    
    # Set file_path on the test submission
    if not hasattr(test_submission, 'file_path') or not test_submission.file_path:
        test_submission.file_path = test_file_path
        
    # Mock the os.path.exists function to return True for our test file
    original_exists = os.path.exists
    original_join = os.path.join
    
    def mock_exists(path):
        if test_file_path in path:
            return True
        return original_exists(path)
    
    # Mock the FileResponse initialization to avoid actually reading a file
    from fastapi.responses import FileResponse
    original_file_response = FileResponse.__init__
    
    def mock_file_response_init(self, path, *args, **kwargs):
        self.path = path
        self.status_code = 200
        
    # Apply monkeypatches
    monkeypatch.setattr(os.path, 'exists', mock_exists)
    monkeypatch.setattr(FileResponse, '__init__', mock_file_response_init)
    
    # Test cases
    
    # Test Case 1: Faculty can download any submission file
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{test_submission.id}/download",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    # Not checking the file content as we mocked the FileResponse
    assert response.status_code == status.HTTP_200_OK
    
    # Test Case 2: Student can download their own submission file
    # Set up a student token that matches the submission's student_id
    student_token = create_access_token({
        "id": str(test_submission.student_id),
        "email": "student@test.com",
        "role": "student"
    })
    
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{test_submission.id}/download",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Test Case 3: Different student cannot download someone else's file
    other_student_token = create_access_token({
        "id": str(uuid.uuid4()),  # Different student ID
        "email": "other_student@test.com",
        "role": "student"
    })
    
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{test_submission.id}/download",
        headers={"Authorization": f"Bearer {other_student_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "You do not have permission to access this file" in response.text
    
    # Test Case 4: Invalid assignment ID
    response = client.get(
        f"/api/v1/assignments/{uuid.uuid4()}/submissions/{test_submission.id}/download",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Submission does not belong to this assignment" in response.text
    
    # Test Case 5: Invalid submission ID
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{uuid.uuid4()}/download",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Submission not found" in response.text
    
    # Test Case 6: Submission without file
    # Temporarily remove file_path
    original_file_path = test_submission.file_path
    test_submission.file_path = None
    
    response = client.get(
        f"/api/v1/assignments/{test_assignment.id}/submissions/{test_submission.id}/download",
        headers={"Authorization": f"Bearer {tokens['faculty']}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "No file found for this submission" in response.text
    
    # Restore file_path for other tests
    test_submission.file_path = original_file_path 