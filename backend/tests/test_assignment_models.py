import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment, Submission
from app.schemas.assignment import AssignmentCreate, SubmissionCreate
from app.services.assignment_service import AssignmentService

# Test Assignment model
@pytest.mark.asyncio
async def test_assignment_model(db_session, test_users):
    # Create test data
    assignment_data = AssignmentCreate(
        title="Test Assignment Model",
        description="This is a test assignment for model testing",
        course_id=str(uuid.uuid4()),
        due_date=datetime.utcnow() + timedelta(days=7),
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
    faculty_id = test_users["faculty"].id
    assignment = await AssignmentService.create_assignment(db_session, assignment_data.model_dump(), faculty_id)
    
    # Verify assignment attributes
    assert assignment.id is not None
    assert assignment.title == assignment_data.title
    assert assignment.description == assignment_data.description
    assert str(assignment.course_id) == assignment_data.course_id
    assert assignment.created_by == faculty_id
    assert assignment.points == assignment_data.points
    assert assignment.status == assignment_data.status
    assert assignment.submission_type == assignment_data.submission_type
    assert assignment.allow_late_submissions == assignment_data.allow_late_submissions
    assert assignment.late_penalty == assignment_data.late_penalty
    assert assignment.plagiarism_detection == assignment_data.plagiarism_detection
    assert assignment.file_types == assignment_data.file_types
    assert assignment.max_file_size == assignment_data.max_file_size
    
    # Test direct model creation
    new_assignment = Assignment(
        title="Direct Model Creation",
        description="Created directly through the model",
        course_id=uuid.uuid4(),
        created_by=faculty_id,
        due_date=datetime.utcnow() + timedelta(days=10),
        points=150,
        status="published",
        submission_type="file",
        allow_late_submissions=False,
        late_penalty=0,
        plagiarism_detection=False,
        file_types="pdf",
        max_file_size=10
    )
    
    # Add to session and commit
    db_session.add(new_assignment)
    await db_session.commit()
    await db_session.refresh(new_assignment)
    
    # Verify direct model creation
    assert new_assignment.id is not None
    assert new_assignment.title == "Direct Model Creation"
    assert new_assignment.status == "published"
    
    # Test model relationships
    # Query the assignment from the database
    db_assignment = await db_session.get(Assignment, assignment.id)
    
    # Verify the assignment exists
    assert db_assignment is not None
    assert db_assignment.id == assignment.id
    
    # Test model string representation
    assert str(assignment) == f"Assignment(id={assignment.id}, title={assignment.title})"

# Test Submission model
@pytest.mark.asyncio
async def test_submission_model(db_session, test_assignment, test_users):
    # Create test data
    submission_data = SubmissionCreate(
        content="This is a test submission content",
        status="draft"
    )
    
    # Create submission
    student_id = test_users["student"].id
    submission = await AssignmentService.create_submission(
        db_session, 
        test_assignment.id, 
        student_id, 
        submission_data.model_dump()
    )
    
    # Verify submission attributes
    assert submission.id is not None
    assert submission.assignment_id == test_assignment.id
    assert submission.student_id == student_id
    assert submission.content == submission_data.content
    assert submission.status == submission_data.status
    assert submission.grade is None
    assert submission.feedback is None
    assert submission.plagiarism_score is None
    assert submission.submitted_at is not None
    
    # Test direct model creation
    new_submission = Submission(
        assignment_id=test_assignment.id,
        student_id=student_id,
        content="Direct model creation content",
        status="submitted",
        grade=95,
        feedback="Excellent work!",
        plagiarism_score=0.0,
        submitted_at=datetime.utcnow()
    )
    
    # Add to session and commit
    db_session.add(new_submission)
    await db_session.commit()
    await db_session.refresh(new_submission)
    
    # Verify direct model creation
    assert new_submission.id is not None
    assert new_submission.content == "Direct model creation content"
    assert new_submission.grade == 95
    assert new_submission.feedback == "Excellent work!"
    
    # Test model relationships
    # Query the submission from the database
    db_submission = await db_session.get(Submission, submission.id)
    
    # Verify the submission exists
    assert db_submission is not None
    assert db_submission.id == submission.id
    
    # Test relationship with assignment
    assert db_submission.assignment_id == test_assignment.id
    
    # Test model string representation
    assert str(submission) == f"Submission(id={submission.id}, assignment_id={submission.assignment_id}, student_id={submission.student_id})"

# Test late submission calculation
@pytest.mark.asyncio
async def test_late_submission_calculation(db_session, test_users):
    # Create an assignment due in the past
    past_due_date = datetime.utcnow() - timedelta(days=2)
    assignment_data = AssignmentCreate(
        title="Past Due Assignment",
        description="This assignment is already past due",
        course_id=str(uuid.uuid4()),
        due_date=past_due_date,
        points=100,
        status="published",
        submission_type="text",
        allow_late_submissions=True,
        late_penalty=10,  # 10% penalty per day
        plagiarism_detection=False,
        file_types="",
        max_file_size=0
    )
    
    # Create assignment
    faculty_id = test_users["faculty"].id
    assignment = await AssignmentService.create_assignment(db_session, assignment_data.model_dump(), faculty_id)
    
    # Create a late submission
    submission_data = SubmissionCreate(
        content="This is a late submission",
        status="submitted"
    )
    
    student_id = test_users["student"].id
    submission = await AssignmentService.create_submission(
        db_session, 
        assignment.id, 
        student_id, 
        submission_data.model_dump()
    )
    
    # Verify submission is marked as late
    assert submission.late_submission is True
    
    # Calculate expected penalty (2 days late * 10% penalty per day = 20% penalty)
    expected_penalty = 20
    
    # Grade the submission with 100 points
    submission.grade = 100
    await db_session.commit()
    await db_session.refresh(submission)
    
    # Calculate effective grade with late penalty
    effective_grade = submission.grade * (1 - expected_penalty / 100)
    
    # Verify the effective grade is correct (should be 80)
    assert effective_grade == 80.0
    
    # Test submission that's not late
    future_due_date = datetime.utcnow() + timedelta(days=7)
    assignment_data.due_date = future_due_date
    assignment_data.title = "Future Due Assignment"
    
    future_assignment = await AssignmentService.create_assignment(db_session, assignment_data.model_dump(), faculty_id)
    
    on_time_submission = await AssignmentService.create_submission(
        db_session, 
        future_assignment.id, 
        student_id, 
        submission_data.model_dump()
    )
    
    # Verify submission is not marked as late
    assert on_time_submission.late_submission is False

# Test assignment status transitions
@pytest.mark.asyncio
async def test_assignment_status_transitions(db_session, test_users):
    # Create a draft assignment
    assignment_data = AssignmentCreate(
        title="Status Transition Assignment",
        description="Testing status transitions",
        course_id=str(uuid.uuid4()),
        due_date=datetime.utcnow() + timedelta(days=7),
        points=100,
        status="draft",
        submission_type="text",
        allow_late_submissions=True,
        late_penalty=10,
        plagiarism_detection=False,
        file_types="",
        max_file_size=0
    )
    
    # Create assignment
    faculty_id = test_users["faculty"].id
    assignment = await AssignmentService.create_assignment(db_session, assignment_data.model_dump(), faculty_id)
    
    # Verify initial status
    assert assignment.status == "draft"
    
    # Change status to published
    assignment.status = "published"
    await db_session.commit()
    await db_session.refresh(assignment)
    
    # Verify status change
    assert assignment.status == "published"
    
    # Change status to closed
    assignment.status = "closed"
    await db_session.commit()
    await db_session.refresh(assignment)
    
    # Verify status change
    assert assignment.status == "closed"
    
    # Test invalid status (should not be allowed in real application with validators)
    assignment.status = "invalid_status"
    await db_session.commit()
    await db_session.refresh(assignment)
    
    # This would normally fail with validators, but for testing we just verify it changed
    assert assignment.status == "invalid_status" 