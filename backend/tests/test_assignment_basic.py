import pytest
from app.models.assignment import Assignment
import uuid
from datetime import datetime, UTC

def test_assignment_model_creation():
    """Test that we can create an Assignment model instance"""
    assignment = Assignment(
        id=uuid.uuid4(),
        title="Test Assignment",
        description="Test Description",
        course_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        due_date=datetime.now(UTC),
        points=100,
        status="draft",
        submission_type="file"
    )
    
    assert assignment.title == "Test Assignment"
    assert assignment.description == "Test Description"
    assert assignment.status == "draft" 