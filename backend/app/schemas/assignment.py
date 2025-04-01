from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class AssignmentCreate(BaseModel):
    """
    Model for creating a new assignment.
    """
    title: str = Field(..., description="Assignment title")
    description: str = Field(..., description="Detailed description of the assignment")
    course_id: str = Field(..., description="ID of the course this assignment belongs to")
    module_id: Optional[str] = Field(None, description="Optional ID of the module this assignment belongs to")
    due_date: datetime = Field(..., description="Deadline for assignment submission")
    points: int = Field(0, description="Maximum points possible for this assignment")
    status: str = Field("draft", description="Assignment status (draft, published, archived)")
    submission_type: str = Field("file", description="Type of submission (file, text, url, media)")
    allow_late_submissions: bool = Field(False, description="Whether late submissions are allowed")
    late_penalty: float = Field(0, description="Percentage penalty per day for late submissions")
    group_submission: bool = Field(False, description="Whether group submissions are allowed")
    max_group_size: int = Field(1, description="Maximum number of students in a group")
    enable_peer_review: bool = Field(False, description="Whether peer review is enabled")
    peer_reviewers_count: int = Field(0, description="Number of peer reviewers per submission")
    peer_review_due_date: Optional[datetime] = Field(None, description="Deadline for peer reviews")
    plagiarism_detection: bool = Field(True, description="Whether plagiarism detection is enabled")
    file_types: str = Field("pdf,doc,docx,txt", description="Comma-separated list of allowed file types")
    max_file_size: int = Field(10, description="Maximum file size in MB")
    settings: Optional[Dict[str, Any]] = Field(None, description="Additional settings as JSON")

class AssignmentUpdate(BaseModel):
    """
    Model for updating an existing assignment.
    """
    title: Optional[str] = Field(None, description="Assignment title")
    description: Optional[str] = Field(None, description="Detailed description of the assignment")
    due_date: Optional[datetime] = Field(None, description="Deadline for assignment submission")
    points: Optional[int] = Field(None, description="Maximum points possible for this assignment")
    status: Optional[str] = Field(None, description="Assignment status (draft, published, archived)")
    submission_type: Optional[str] = Field(None, description="Type of submission (file, text, url, media)")
    allow_late_submissions: Optional[bool] = Field(None, description="Whether late submissions are allowed")
    late_penalty: Optional[float] = Field(None, description="Percentage penalty per day for late submissions")
    group_submission: Optional[bool] = Field(None, description="Whether group submissions are allowed")
    max_group_size: Optional[int] = Field(None, description="Maximum number of students in a group")
    enable_peer_review: Optional[bool] = Field(None, description="Whether peer review is enabled")
    peer_reviewers_count: Optional[int] = Field(None, description="Number of peer reviewers per submission")
    peer_review_due_date: Optional[datetime] = Field(None, description="Deadline for peer reviews")
    plagiarism_detection: Optional[bool] = Field(None, description="Whether plagiarism detection is enabled")
    file_types: Optional[str] = Field(None, description="Comma-separated list of allowed file types")
    max_file_size: Optional[int] = Field(None, description="Maximum file size in MB")
    settings: Optional[Dict[str, Any]] = Field(None, description="Additional settings as JSON")

class SubmissionCreate(BaseModel):
    """
    Model for creating a new submission.
    """
    assignment_id: Optional[str] = Field(None, description="ID of the assignment this submission is for")
    content: Optional[str] = Field(None, description="Text content of the submission (for text submissions)")
    url: Optional[str] = Field(None, description="URL for the submission (for url submissions)")
    status: str = Field("draft", description="Submission status (draft, submitted)")

class GradeSubmission(BaseModel):
    """
    Model for grading a submission.
    """
    grade: float = Field(..., description="Numeric grade assigned to the submission")
    feedback: Optional[str] = Field(None, description="Feedback text from the instructor") 