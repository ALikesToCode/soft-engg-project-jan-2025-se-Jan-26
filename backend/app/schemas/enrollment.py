from typing import Optional, List, Dict, Any
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from enum import Enum

class EnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    COMPLETED = "completed"
    DROPPED = "dropped"
    WAITLISTED = "waitlisted"

class EnrollmentCreate(BaseModel):
    course_id: UUID4
    student_id: UUID4
    status: EnrollmentStatus = EnrollmentStatus.ENROLLED
    enrollment_date: datetime = Field(default_factory=datetime.now)

class EnrollmentUpdate(BaseModel):
    status: Optional[EnrollmentStatus] = None
    progress: Optional[float] = None
    grade: Optional[str] = None
    completion_date: Optional[datetime] = None
    certificate_url: Optional[str] = None
    is_favorited: Optional[bool] = None

class EnrollmentBase(BaseModel):
    id: UUID4
    course_id: UUID4
    student_id: UUID4
    status: EnrollmentStatus
    enrollment_date: datetime
    progress: Optional[float] = None
    grade: Optional[str] = None
    completion_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    certificate_url: Optional[str] = None
    is_favorited: Optional[bool] = False

class StudentInfo(BaseModel):
    id: UUID4
    name: str
    email: str
    avatar: Optional[str] = None
    last_activity: datetime
    status: EnrollmentStatus

class StudentProgress(BaseModel):
    student_id: UUID4
    progress: str #float
    last_activity: Optional[datetime] = None
    total_assignments: int
    completed_assignments: int

class AssignmentCompletion(BaseModel):
    id: UUID4
    title: str
    submitted_at: Optional[datetime] = None
    status: Optional[str] = None
    grade: Optional[str] = None
    graded_at: Optional[datetime] = None

class EnrollmentDetail(EnrollmentBase):
    name: str
    email: str
    picture: Optional[str] = None
    assignments: List[AssignmentCompletion] = []

    class Config:
        from_attributes = True 