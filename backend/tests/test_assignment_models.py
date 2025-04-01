import pytest
import uuid
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment, Submission
from app.schemas.assignment import AssignmentCreate, SubmissionCreate
from app.services.assignment_service import AssignmentService

# Test Assignment model
@pytest.mark.asyncio
async def test_assignment_model():
    """Test creating an assignment model"""
    # Create test data
    assignment_data = AssignmentCreate(
        title="Test Assignment",
        description="This is a test assignment",
        course_id=str(uuid.uuid4()),
        due_date=datetime.now(UTC) + timedelta(days=7),
        points=100,
        status="draft",
        submission_type="text",
        allow_late_submissions=True,
        late_penalty=10,
        plagiarism_detection=True,
        file_types="pdf,doc,docx",
        max_file_size=5
    )
    
    # Create assignment directly
    assignment = Assignment(
        id=uuid.uuid4(),
        title=assignment_data.title,
        description=assignment_data.description,
        course_id=uuid.UUID(assignment_data.course_id),
        created_by=uuid.uuid4(),  # Simulate a faculty ID
        due_date=assignment_data.due_date,
        points=assignment_data.points,
        status=assignment_data.status,
        submission_type=assignment_data.submission_type,
        allow_late_submissions=assignment_data.allow_late_submissions,
        late_penalty=assignment_data.late_penalty,
        plagiarism_detection=assignment_data.plagiarism_detection,
        file_types=assignment_data.file_types,
        max_file_size=assignment_data.max_file_size
    )
    
    # Verify assignment attributes
    assert assignment.id is not None
    assert assignment.title == assignment_data.title
    assert assignment.description == assignment_data.description
    assert str(assignment.course_id) == assignment_data.course_id
    assert assignment.points == assignment_data.points
    assert assignment.status == assignment_data.status
    assert assignment.submission_type == assignment_data.submission_type
    assert assignment.allow_late_submissions == assignment_data.allow_late_submissions
    assert assignment.late_penalty == assignment_data.late_penalty
    assert assignment.plagiarism_detection == assignment_data.plagiarism_detection
    assert assignment.file_types == assignment_data.file_types
    assert assignment.max_file_size == assignment_data.max_file_size

# Test Submission model
@pytest.mark.asyncio
async def test_submission_model():
    """Test creating a submission model"""
    # Create test assignment
    assignment_id = uuid.uuid4()
    student_id = uuid.uuid4()
    
    # Create test data
    submission_data = SubmissionCreate(
        content="This is a test submission",
        status="submitted"
    )
    
    # Create submission directly
    submission = Submission(
        id=uuid.uuid4(),
        assignment_id=assignment_id,
        student_id=student_id,
        content=submission_data.content,
        status=submission_data.status,
        submitted_at=datetime.now(UTC)
    )
    
    # Verify submission attributes
    assert submission.id is not None
    assert submission.assignment_id == assignment_id
    assert submission.student_id == student_id
    assert submission.content == submission_data.content
    assert submission.status == submission_data.status
    assert submission.submitted_at is not None

# Test late submission calculation
@pytest.mark.asyncio
async def test_late_submission_calculation(db_session, test_users):
    """Test calculation of late submission status"""
    # Ensure test_users is awaited if it's a coroutine
    users = await test_users if isinstance(test_users, object) and hasattr(test_users, "__await__") else test_users
    
    # Create an assignment due in the past
    due_date = datetime.now(UTC) - timedelta(days=1)
    assignment_data = AssignmentCreate(
        title="Late Submission Test",
        description="Test assignment for late submission",
        course_id=str(uuid.uuid4()),
        due_date=due_date,
        points=100,
        status="published",
        submission_type="text",
        allow_late_submissions=True,
        late_penalty=10,
        plagiarism_detection=True,
        file_types="pdf,doc,docx",
        max_file_size=5
    )
    
    # Create assignment
    faculty_id = users["faculty"].id
    assignment_coroutine = AssignmentService.create_assignment(db_session, assignment_data.model_dump(), faculty_id)
    assignment = await assignment_coroutine
    
    # Create a submission after the due date
    submission_data = SubmissionCreate(
        content="This is a late submission",
        status="submitted"
    )
    
    # Create submission
    student_id = users["student"].id
    submission_coroutine = AssignmentService.create_submission(
        db_session, 
        assignment.id, 
        student_id, 
        submission_data.model_dump()
    )
    submission = await submission_coroutine
    
    # Verify submission is marked as late
    assert submission.is_late is True
    
    # Calculate late penalty
    expected_penalty = assignment.late_penalty
    assert submission.late_penalty == expected_penalty

# Test assignment status transitions
@pytest.mark.asyncio
async def test_assignment_status_transitions(db_session, test_users):
    """Test assignment status transitions"""
    # Ensure test_users is awaited if it's a coroutine
    users = await test_users if isinstance(test_users, object) and hasattr(test_users, "__await__") else test_users
    
    # Create a draft assignment
    assignment_data = AssignmentCreate(
        title="Status Transition Test",
        description="Test assignment for status transitions",
        course_id=str(uuid.uuid4()),
        due_date=datetime.now(UTC) + timedelta(days=7),
        points=100,
        status="draft",
        submission_type="text",
        allow_late_submissions=True,
        late_penalty=10,
        plagiarism_detection=True,
        file_types="pdf,doc,docx",
        max_file_size=5
    )
    
    # Create assignment
    faculty_id = users["faculty"].id
    assignment_coroutine = AssignmentService.create_assignment(db_session, assignment_data.model_dump(), faculty_id)
    assignment = await assignment_coroutine
    
    # Verify initial status
    assert assignment.status == "draft"
    
    # Transition to published
    update_data = {"status": "published"}
    updated_assignment_coroutine = AssignmentService.update_assignment(db_session, assignment.id, update_data)
    updated_assignment = await updated_assignment_coroutine
    
    # Verify status change
    assert updated_assignment.status == "published"
    
    # Transition to archived
    update_data = {"status": "archived"}
    archived_assignment_coroutine = AssignmentService.update_assignment(db_session, assignment.id, update_data)
    archived_assignment = await archived_assignment_coroutine
    
    # Verify status change
    assert archived_assignment.status == "archived" 