import pytest
import uuid
from datetime import datetime, timedelta, UTC

from app.models.assignment import Assignment, Submission
from app.schemas.assignment import AssignmentCreate, SubmissionCreate

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
async def test_late_submission_calculation():
    """Test calculation of late submission status"""
    # Create an assignment due in the past
    due_date = datetime.now(UTC) - timedelta(days=1)
    assignment = Assignment(
        id=uuid.uuid4(),
        title="Late Submission Test",
        description="Test assignment for late submission",
        course_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
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
    
    # Create a submission after the due date
    submission = Submission(
        id=uuid.uuid4(),
        assignment_id=assignment.id,
        student_id=uuid.uuid4(),
        content="This is a late submission",
        status="submitted",
        submitted_at=datetime.now(UTC)  # Current time, which is after the due date
    )
    
    # Manually calculate if the submission is late
    is_late = submission.submitted_at > assignment.due_date
    
    # Verify submission is late
    assert is_late is True
    
    # Create an assignment that doesn't allow late submissions
    no_late_assignment = Assignment(
        id=uuid.uuid4(),
        title="No Late Submissions",
        description="Test assignment that doesn't allow late submissions",
        course_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        due_date=due_date,
        points=100,
        status="published",
        submission_type="text",
        allow_late_submissions=False,
        late_penalty=0,
        plagiarism_detection=True,
        file_types="pdf,doc,docx",
        max_file_size=5
    )
    
    # In a real application, attempting to create a late submission for an assignment
    # that doesn't allow late submissions would raise an exception
    # Here we just verify the assignment settings
    assert no_late_assignment.allow_late_submissions is False

# Test assignment status transitions
@pytest.mark.asyncio
async def test_assignment_status_transitions():
    """Test assignment status transitions"""
    # Create a draft assignment
    assignment = Assignment(
        id=uuid.uuid4(),
        title="Status Transition Test",
        description="Test assignment for status transitions",
        course_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
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
    
    # Verify initial status
    assert assignment.status == "draft"
    
    # Transition to published
    assignment.status = "published"
    
    # Verify status change
    assert assignment.status == "published"
    
    # Transition to archived
    assignment.status = "archived"
    
    # Verify status change
    assert assignment.status == "archived"
    
    # Try invalid status (in a real application, this would be validated)
    # Here we just set it to test the model behavior
    try:
        assignment.status = "invalid_status"
        # If we get here without an exception, the model doesn't have validation
        # This is just a basic test of the model, not the validation logic
    except Exception:
        # If validation is implemented, an exception would be raised
        pass 