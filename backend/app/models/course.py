from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Table, Text, UniqueConstraint, LargeBinary
from sqlalchemy.orm import relationship
from app.database import Base, engine, UUID
from app.models.assignment import Assignment
from datetime import datetime, UTC
import enum
import uuid

# Enums for course and enrollment status
class CourseStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active" 
    ARCHIVED = "archived"

class EnrollmentStatus(str, enum.Enum):
    ENROLLED = "enrolled"
    COMPLETED = "completed"
    DROPPED = "dropped"
    WAITLISTED = "waitlisted"

# Association table for many-to-many relationship between users and courses
user_courses = Table(
    "user_courses",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", UUID, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)

# Course Model
class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    syllabus = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    credits = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)  # e.g., Weeks or Months
    semester = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(Enum(CourseStatus), nullable=False, default=CourseStatus.DRAFT)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    enrollment_limit = Column(Integer, nullable=True)
    waitlist_limit = Column(Integer, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    created_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    faculty_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Relationships
    faculty = relationship("User", foreign_keys=[faculty_id], back_populates="courses_taught")
    creator = relationship("User", foreign_keys=[created_by])
    users = relationship("User", secondary=user_courses, back_populates="courses")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "title": self.title,
            "syllabus": self.syllabus,
            "description": self.description,
            "credits": self.credits,
            "duration": self.duration,
            "semester": self.semester,
            "year": self.year,
            "status": self.status.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "enrollment_limit": self.enrollment_limit,
            "waitlist_limit": self.waitlist_limit,
            "image": self.image,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID, ForeignKey("courses.id"), nullable=False)
    student_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.ENROLLED)
    enrollment_date = Column(DateTime, nullable=False, default=datetime.now(UTC))
    completion_date = Column(DateTime)
    grade = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    course = relationship("Course", back_populates="enrollments")
    student = relationship("User", back_populates="course_enrollments")

# Module Model (Course → Modules)
class Module(Base):
    __tablename__ = "module"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(UUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)  # e.g., "Week 1"
    position = Column(Integer, nullable=False)  # Ordering field
    course = relationship("Course", back_populates="modules")
    lectures = relationship("Lecture", back_populates="module", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("course_id", "position", name="module_position_unique"),)

    def to_dict(self):
        return {
            "id": str(self.id),
            "course_id": str(self.course_id),
            "title": self.title,
            "position": self.position,
        }

# Lecture Model (Module → Lectures)
class Lecture(Base):
    __tablename__ = "lecture"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("module.id", ondelete="CASCADE"), nullable=False)
    content_type = Column(String(50), nullable=False)  # 'lecture', 'quiz', 'assignment', document
    position = Column(Integer, nullable=False)  # 1= lecture 1, 2= lecture 2, etc.
    module = relationship("Module", back_populates="lectures")
    contents = relationship("LectureContent", back_populates="lecture", cascade="all, delete-orphan")
    contents_doc = relationship("LectureContentDoc", back_populates="lecture", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id),
            "module_id": str(self.module_id),
            "content_type": self.content_type,
            "lecture_number": str(self.position),
        }

# Lecture Content Model (Lecture → Content)
class LectureContent(Base):
    __tablename__ = "lecture_content"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lecture_id = Column(Integer, ForeignKey("lecture.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False) # e.g., "Introduction to Python"
    content_url = Column(Text, nullable=False)  # e.g., YouTube link or PDF URL
    content_desc = Column(Text, nullable=True)

    lecture = relationship("Lecture", back_populates="contents")

    def to_dict(self):
        return {
            "id": str(self.id),
            "lecture_id": str(self.lecture_id),
            "lecture_title": str(self.title),
            "content_url": self.content_url,
            "content_desc": self.content_desc,
        }

# Lecture Content Model (Lecture → LectureContentDoc)
class LectureContentDoc(Base):
    __tablename__ = "lecture_content_doc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lecture_id = Column(Integer, ForeignKey("lecture.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)  # e.g., "Introduction to Python"
    content_desc = Column(Text, nullable=True)
    content_doc = Column(String, nullable=False)  # Stores path of the file content (PDF, DOC, PPT, PPTX)
    file_type = Column(String, nullable=False)  # Stores MIME type (e.g., application/pdf, application/vnd.ms-powerpoint)

    lecture = relationship("Lecture", back_populates="contents_doc")

    def to_dict(self):
        return {
            "id": str(self.id),
            "lecture_id": str(self.lecture_id),
            "lecture_title": self.title,
            "file_type": self.file_type,
            "driveLink": self.content_doc,
            "content_desc": self.content_desc,
        }

# Initialize Database Tables
async def init_db():
    """Initialize the database tables asynchronously."""
    async with engine.begin() as conn:
        # Drop all tables first to ensure clean state
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
