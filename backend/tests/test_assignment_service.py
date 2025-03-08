import pytest
import uuid
import os
from datetime import datetime, timedelta, UTC
from fastapi import UploadFile, HTTPException
from io import BytesIO

from app.services.assignment_service import AssignmentService
from app.models.assignment import Assignment, Submission

# Mock file for testing
class MockUploadFile:
    def __init__(self, filename="test.txt", content_type="text/plain", content=b"Test content"):
        self.filename = filename
        self._content_type = content_type
        self._content = BytesIO(content)
        self.size = len(content)
    
    @property
    def content_type(self):
        return self._content_type
    
    async def read(self):
        return self._content.getvalue()

# Test assignment creation
@pytest.mark.asyncio
async def test_create_assignment(db_session, test_users):
    # Prepare test data
    assignment_data = {
        "title": "Test Assignment Creation",
        "description": "This is a test assignment for creation",
        "course_id": uuid.uuid4(),
        "due_date": datetime.now(UTC) + timedelta(days=7),
        "points": 100,
        "status": "draft",
        "submission_type": "file"
    }
    
    # Create assignment
    assignment = await AssignmentService.create_assignment(
        db_session, 
        assignment_data, 
        test_users["faculty"].id
    )
    
    # Verify assignment was created
    assert assignment is not None
    assert assignment.title == assignment_data["title"]
    assert assignment.description == assignment_data["description"]
    assert assignment.course_id == assignment_data["course_id"]
    assert assignment.created_by == test_users["faculty"].id
    assert assignment.status == "draft"

# Test get assignment
@pytest.mark.asyncio
async def test_get_assignment(db_session, test_assignment):
    # Get assignment
    assignment = await AssignmentService.get_assignment(db_session, test_assignment.id)
    
    # Verify assignment was retrieved
    assert assignment is not None
    assert assignment.id == test_assignment.id
    assert assignment.title == test_assignment.title
    assert assignment.description == test_assignment.description

# Test get assignments by course
@pytest.mark.asyncio
async def test_get_assignments_by_course(db_session, test_assignment):
    # Get assignments by course
    assignments = await AssignmentService.get_assignments_by_course(db_session, test_assignment.course_id)
    
    # Verify assignments were retrieved
    assert assignments is not None
    assert len(assignments) > 0
    assert any(a.id == test_assignment.id for a in assignments)

# Test update assignment
@pytest.mark.asyncio
async def test_update_assignment(db_session, test_assignment):
    # Prepare update data
    update_data = {
        "title": "Updated Assignment Title",
        "description": "Updated assignment description",
        "points": 150
    }
    
    # Update assignment
    updated_assignment = await AssignmentService.update_assignment(
        db_session, 
        test_assignment.id, 
        update_data
    )
    
    # Verify assignment was updated
    assert updated_assignment is not None
    assert updated_assignment.id == test_assignment.id
    assert updated_assignment.title == update_data["title"]
    assert updated_assignment.description == update_data["description"]
    assert updated_assignment.points == update_data["points"]
    # Verify other fields remain unchanged
    assert updated_assignment.course_id == test_assignment.course_id
    assert updated_assignment.created_by == test_assignment.created_by

# Test delete assignment
@pytest.mark.asyncio
async def test_delete_assignment(db_session, test_assignment):
    # Delete assignment
    result = await AssignmentService.delete_assignment(db_session, test_assignment.id)
    
    # Verify assignment was deleted
    assert result is True
    
    # Verify assignment no longer exists
    deleted_assignment = await AssignmentService.get_assignment(db_session, test_assignment.id)
    assert deleted_assignment is None

# Test create submission
@pytest.mark.asyncio
async def test_create_submission(db_session, test_assignment, test_users):
    # Prepare submission data
    submission_data = {
        "content": "This is a test submission content",
        "status": "draft"
    }
    
    # Create submission
    submission = await AssignmentService.create_submission(
        db_session,
        test_assignment.id,
        test_users["student"].id,
        submission_data
    )
    
    # Verify submission was created
    assert submission is not None
    assert submission.assignment_id == test_assignment.id
    assert submission.student_id == test_users["student"].id
    assert submission.content == submission_data["content"]
    assert submission.status == "draft"
    assert submission.submitted_at is None  # Draft submissions don't have submitted_at

# Test create submission with file
@pytest.mark.asyncio
async def test_create_submission_with_file(db_session, test_assignment, test_users):
    # Prepare submission data
    submission_data = {
        "status": "submitted"
    }

    # Create mock file
    mock_file = MockUploadFile(
        filename="test_submission.txt",
        content_type="text/plain",
        content=b"This is a test submission file content"
    )

    # Create submission
    submission = await AssignmentService.create_submission(
        db_session,
        test_assignment.id,
        test_users["student"].id,
        submission_data,
        mock_file
    )

    # Verify submission was created
    assert submission is not None
    assert submission.id is not None
    assert submission.assignment_id == test_assignment.id
    assert submission.student_id == test_users["student"].id
    assert submission.status == "submitted"
    assert submission.file_name == "test_submission.txt"
    assert submission.file_type == "text/plain"
    assert submission.file_size == len(b"This is a test submission file content")
    assert submission.submitted_at is not None

    # Verify file was saved
    if not os.environ.get("TESTING"):
        assert os.path.exists(submission.file_path)
        
        # Clean up test file
        try:
            os.remove(submission.file_path)
        except:
            pass

# Test get submission
@pytest.mark.asyncio
async def test_get_submission(db_session, test_submission):
    # Get submission
    submission = await AssignmentService.get_submission(db_session, test_submission.id)
    
    # Verify submission was retrieved
    assert submission is not None
    assert submission.id == test_submission.id
    assert submission.assignment_id == test_submission.assignment_id
    assert submission.student_id == test_submission.student_id
    assert submission.content == test_submission.content

# Test get submissions by assignment
@pytest.mark.asyncio
async def test_get_submissions_by_assignment(db_session, test_assignment, test_submission):
    # Get submissions by assignment
    submissions = await AssignmentService.get_submissions_by_assignment(db_session, test_assignment.id)
    
    # Verify submissions were retrieved
    assert submissions is not None
    assert len(submissions) > 0
    assert any(s.id == test_submission.id for s in submissions)

# Test get student submission
@pytest.mark.asyncio
async def test_get_student_submission(db_session, test_assignment, test_submission, test_users):
    # Get student submission
    submission = await AssignmentService.get_student_submission(
        db_session, 
        test_assignment.id, 
        test_users["student"].id
    )
    
    # Verify submission was retrieved
    assert submission is not None
    assert submission.id == test_submission.id
    assert submission.assignment_id == test_assignment.id
    assert submission.student_id == test_users["student"].id

# Test grade submission
@pytest.mark.asyncio
async def test_grade_submission(db_session, test_submission, test_users):
    # Prepare grade data
    grade_data = {
        "grade": 85,
        "feedback": "Good work, but could improve code organization"
    }
    
    # Grade submission
    graded_submission = await AssignmentService.grade_submission(
        db_session,
        test_submission.id,
        grade_data,
        test_users["faculty"].id
    )
    
    # Verify submission was graded
    assert graded_submission is not None
    assert graded_submission.id == test_submission.id
    assert graded_submission.grade == grade_data["grade"]
    assert graded_submission.feedback == grade_data["feedback"]
    assert graded_submission.graded_by == test_users["faculty"].id
    assert graded_submission.graded_at is not None
    assert graded_submission.status == "graded"

# Test plagiarism check
@pytest.mark.asyncio
async def test_plagiarism_check(db_session, test_assignment, test_users):
    # Create two similar submissions
    submission1_data = {
        "content": "This is a test submission with similar content",
        "status": "submitted"
    }
    
    submission2_data = {
        "content": "This is a test submission with similar content",
        "status": "submitted"
    }
    
    # Create first submission
    submission1 = await AssignmentService.create_submission(
        db_session,
        test_assignment.id,
        test_users["student"].id,
        submission1_data
    )
    
    # Create second submission with different student (using faculty ID as a stand-in)
    submission2 = Submission(
        id=uuid.uuid4(),
        assignment_id=test_assignment.id,
        student_id=test_users["faculty"].id,  # Using faculty as another student for this test
        submitted_at=datetime.now(UTC),
        status="submitted",
        content=submission2_data["content"]
    )
    
    db_session.add(submission2)
    await db_session.commit()
    await db_session.refresh(submission2)
    
    # Run plagiarism check on first submission
    checked_submission = await AssignmentService.check_plagiarism(db_session, submission1)
    
    # Verify plagiarism check results
    assert checked_submission is not None
    assert checked_submission.plagiarism_score is not None
    assert checked_submission.plagiarism_score > 0  # Should detect similarity
    assert checked_submission.plagiarism_report is not None 