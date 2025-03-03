from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.assignment import Assignment
import uuid
from datetime import datetime
import enum

class CourseStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

class EnrollmentStatus(str, enum.Enum):
    ENROLLED = "enrolled"
    COMPLETED = "completed"
    DROPPED = "dropped"
    WAITLISTED = "waitlisted"

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    description = Column(String)
    credits = Column(Integer, nullable=False)
    semester = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(Enum(CourseStatus), nullable=False, default=CourseStatus.DRAFT)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    faculty = relationship("User", foreign_keys=[faculty_id], back_populates="courses_taught")
    creator = relationship("User", foreign_keys=[created_by])
    enrollments = relationship("CourseEnrollment", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.ENROLLED)
    enrollment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    completion_date = Column(DateTime)
    grade = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="enrollments")
    student = relationship("User", back_populates="course_enrollments") 