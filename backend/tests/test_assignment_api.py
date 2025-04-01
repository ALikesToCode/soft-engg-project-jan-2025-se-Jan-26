import pytest
import uuid
import json
from datetime import datetime, timedelta, UTC
from fastapi import status
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Test assignment creation
@pytest.mark.asyncio
async def test_create_assignment(client: TestClient, tokens):
    # Login as faculty
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['faculty']}"}
    
    # Create test assignment data
    assignment_data = {
        "title": "API Test Assignment",
        "description": "This is a test assignment created via API",
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
    
    # Send request to create assignment
    response = await client.post(
        "/api/v1/assignments",
        headers=headers,
        json=assignment_data
    ) if isinstance(client, AsyncClient) else client.post(
        "/api/v1/assignments",
        headers=headers,
        json=assignment_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "assignment_id" in data
    assert data["message"] == "Assignment created successfully"
    
    # Store assignment ID for later tests
    return data["assignment_id"]

# Test getting assignments for a course
@pytest.mark.asyncio
async def test_get_assignments(client: TestClient, tokens):
    # Login as faculty
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['faculty']}"}
    
    # Create a test assignment first
    assignment_id = await test_create_assignment(client, tokens)
    
    # Get the course ID from the created assignment
    response = client.get(
        f"/api/v1/assignments/{assignment_id}",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    assignment = response.json()
    course_id = assignment["course_id"]
    
    # Get assignments for the course
    response = client.get(
        f"/api/v1/assignments?course_id={course_id}",
        headers=headers
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    assignments = response.json()
    assert isinstance(assignments, list)
    assert len(assignments) >= 1
    
    # Verify the created assignment is in the list
    assignment_ids = [a["id"] for a in assignments]
    assert assignment_id in assignment_ids

# Test getting a specific assignment
@pytest.mark.asyncio
async def test_get_assignment(client: TestClient, tokens):
    # Login as faculty
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['faculty']}"}
    
    # Create a test assignment first
    assignment_id = await test_create_assignment(client, tokens)
    
    # Get the assignment
    response = client.get(
        f"/api/v1/assignments/{assignment_id}",
        headers=headers
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    assignment = response.json()
    assert assignment["id"] == assignment_id
    assert assignment["title"] == "API Test Assignment"

# Test updating an assignment
@pytest.mark.asyncio
async def test_update_assignment(client: TestClient, tokens):
    # Login as faculty
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['faculty']}"}
    
    # Create a test assignment first
    assignment_id = await test_create_assignment(client, tokens)
    
    # Update data
    update_data = {
        "title": "Updated Assignment Title",
        "description": "This assignment has been updated via API",
        "points": 150
    }
    
    # Send update request
    response = client.put(
        f"/api/v1/assignments/{assignment_id}",
        headers=headers,
        json=update_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Assignment updated successfully"
    
    # Verify the update was applied
    response = client.get(
        f"/api/v1/assignments/{assignment_id}",
        headers=headers
    )
    updated_assignment = response.json()
    assert updated_assignment["title"] == update_data["title"]
    assert updated_assignment["description"] == update_data["description"]
    assert updated_assignment["points"] == update_data["points"]

# Test submitting an assignment
@pytest.mark.asyncio
async def test_submit_assignment(client: TestClient, tokens):
    # Login as faculty to create assignment
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['faculty']}"}
    
    # Create test assignment
    assignment_id = await test_create_assignment(client, tokens)
    
    # Login as student to submit
    student_headers = {"Authorization": f"Bearer {token_data['student']}"}
    
    # Prepare submission data
    submission_data = {
        "content": "This is my submission for the test assignment",
        "status": "submitted"
    }
    
    # Send submission request
    response = client.post(
        f"/api/v1/assignments/{assignment_id}/submit",
        headers=student_headers,
        data=submission_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "submission_id" in data
    assert data["message"] == "Assignment submitted successfully"
    
    # Store submission ID for later tests
    return data["submission_id"]

# Test getting student's submission
@pytest.mark.asyncio
async def test_get_my_submission(client: TestClient, tokens):
    # Login as faculty to create assignment
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['faculty']}"}
    
    # Create test assignment
    assignment_id = await test_create_assignment(client, tokens)
    
    # Login as student to submit
    student_headers = {"Authorization": f"Bearer {token_data['student']}"}
    
    # Submit the assignment
    await test_submit_assignment(client, tokens)
    
    # Get student's submission
    response = client.get(
        f"/api/v1/assignments/{assignment_id}/my-submission",
        headers=student_headers
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    submission = response.json()
    assert submission["assignment_id"] == assignment_id
    assert submission["content"] == "This is my submission for the test assignment"
    assert submission["status"] == "submitted"

# Test grading a submission
@pytest.mark.asyncio
async def test_grade_submission(client: TestClient, tokens):
    # Login as faculty
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['faculty']}"}
    
    # Create test assignment
    assignment_id = await test_create_assignment(client, tokens)
    
    # Login as student to submit
    student_headers = {"Authorization": f"Bearer {token_data['student']}"}
    
    # Submit the assignment
    submission_id = await test_submit_assignment(client, tokens)
    
    # Grade the submission
    grade_data = {
        "grade": 95.5,
        "feedback": "Excellent work on this assignment!"
    }
    
    # Send grading request
    response = client.put(
        f"/api/v1/assignments/{assignment_id}/grade/{submission_id}",
        headers=headers,
        json=grade_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Submission graded successfully"
    
    # Verify the grade was applied
    response = client.get(
        f"/api/v1/assignments/{assignment_id}/my-submission",
        headers=student_headers
    )
    graded_submission = response.json()
    assert graded_submission["grade"] == grade_data["grade"]
    assert graded_submission["feedback"] == grade_data["feedback"]

# Test deleting an assignment
@pytest.mark.asyncio
async def test_delete_assignment(client: TestClient, tokens):
    # Login as faculty
    token_data = await tokens if isinstance(tokens, object) and hasattr(tokens, "__await__") else tokens
    headers = {"Authorization": f"Bearer {token_data['faculty']}"}
    
    # Create a test assignment first
    assignment_id = await test_create_assignment(client, tokens)
    
    # Send delete request
    response = client.delete(
        f"/api/v1/assignments/{assignment_id}",
        headers=headers
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Assignment deleted successfully"
    
    # Verify the assignment was deleted
    response = client.get(
        f"/api/v1/assignments/{assignment_id}",
        headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND 