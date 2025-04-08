from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Table, Text, UniqueConstraint, LargeBinary, Float, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base, engine, UUID
from app.models.assignment import Assignment
from datetime import datetime, UTC
import enum
import uuid
from sqlalchemy.dialects.postgresql import ENUM

# Enums for course and enrollment status
class CourseStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE" 
    ARCHIVED = "ARCHIVED"

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
    """
    Course model representing academic courses in the system.
    
    This model stores information about courses including their syllabus, 
    enrollment details, status, and relationships to instructors and students.
    
    Attributes:
        id: Unique UUID primary key for the course
        name: Course name
        code: Unique course code used for registration
        title: Course title displayed to users
        syllabus: Course syllabus document
        description: Detailed course description
        credits: Number of academic credits for the course
        status: Current status of the course (DRAFT, ACTIVE, ARCHIVED)
        faculty_id: ID of the faculty member teaching the course
        created_by: ID of the user who created the course
        created_at: Timestamp when the course record was created
        updated_at: Timestamp when the course record was last updated
    """
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
    # Use String type with enum validation instead of PostgreSQL ENUM type
    # status = Column(String, nullable=False, default=CourseStatus.DRAFT.value)
    status = Column(ENUM(CourseStatus, name="coursestatus"), nullable=False, default=CourseStatus.DRAFT)
    level = Column(String, nullable=True, default="Beginner")
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    enrollment_limit = Column(Integer, nullable=True)
    waitlist_limit = Column(Integer, nullable=True)
    capacity = Column(Integer, nullable=True, default=50)  # Maximum number of students allowed
    enrolled_count = Column(Integer, nullable=False, default=0)  # Current number of enrolled students
    image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))
    created_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    faculty_id = Column(UUID, ForeignKey("users.id"), nullable=True)  # Making this nullable since faculty may not be assigned initially

    # Relationships
    faculty = relationship("User", foreign_keys=[faculty_id], back_populates="courses_taught")
    creator = relationship("User", foreign_keys=[created_by])
    users = relationship("User", secondary=user_courses, back_populates="courses")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

    # Add indexes for frequently queried fields
    __table_args__ = (
        Index('idx_course_status', 'status'),
        Index('idx_course_faculty', 'faculty_id'),
        Index('idx_course_created_by', 'created_by'),
        Index('idx_course_semester_year', 'semester', 'year'),
    )

    def to_dict(self, detail_level="basic"):
        """
        Convert course model to dictionary representation with configurable detail levels.
        
        Args:
            detail_level (str): Level of detail to include:
                - "basic": Only core information
                - "standard": Standard course details
                - "full": All course information including related objects
        
        Returns:
            dict: Dictionary representation of the course
        """
        # Basic information always included
        data = {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "title": self.title,
            "status": self.status.value if hasattr(self.status, 'value') else self.status,
            "faculty_id": str(self.faculty_id) if self.faculty_id else None,
            "enrolled_count": self.enrolled_count,
            "capacity": self.capacity,
        }
        
        # Add standard details
        if detail_level in ["standard", "full"]:
            data.update({
                "description": self.description,
                "credits": self.credits,
                "duration": self.duration,
                "semester": self.semester,
                "year": self.year,
                "level": self.level,
                "start_date": self.start_date.isoformat() if self.start_date else None,
                "end_date": self.end_date.isoformat() if self.end_date else None,
                "enrollment_limit": self.enrollment_limit,
                "waitlist_limit": self.waitlist_limit,
                "image": self.image,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            })
        
        # Add full details including relationships
        if detail_level == "full":
            if self.faculty:
                data["faculty"] = {
                    "id": str(self.faculty.id),
                    "name": self.faculty.name,
                    "email": self.faculty.email
                }
            
            if self.modules:
                data["modules"] = [module.to_dict() for module in self.modules]
            
            if self.assignments:
                data["assignments"] = [
                    {
                        "id": str(assignment.id),
                        "title": assignment.title,
                        "due_date": assignment.due_date.isoformat() if assignment.due_date else None
                    }
                    for assignment in self.assignments
                ]
        
        return data

class CourseEnrollment(Base):
    """
    CourseEnrollment model tracking student enrollment in courses.
    
    This model stores information about a student's enrollment status,
    grades, and progress in a specific course.
    
    Attributes:
        id: Unique UUID primary key for the enrollment
        course_id: ID of the course
        student_id: ID of the enrolled student
        user_id: ID of the user (same as student_id, kept for compatibility)
        status: Current enrollment status (ENROLLED, COMPLETED, DROPPED, WAITLISTED)
        enrollment_date: Date when the student enrolled
        completion_date: Date when the student completed the course
        grade: Student's grade in the course
        progress: Student's progress percentage in the course
    """
    __tablename__ = "course_enrollments"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(ENUM(EnrollmentStatus, name="enrollmentstatus"), nullable=False, default=EnrollmentStatus.ENROLLED)
    enrollment_date = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    completion_date = Column(DateTime(timezone=True))
    grade = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    certificate_url = Column(String, nullable=True)
    progress = Column(Float, default=0.0)  # Percentage of course completed (0-100)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_favorited = Column(Boolean, default=False)

    # Relationships
    course = relationship("Course", back_populates="enrollments")
    student = relationship("User", foreign_keys=[student_id], back_populates="course_enrollments")
    user = relationship("User", foreign_keys=[user_id], back_populates="enrollments")

    # Add indexes for frequently queried fields
    __table_args__ = (
        Index('idx_enrollment_course', 'course_id'),
        Index('idx_enrollment_student', 'student_id'),
        Index('idx_enrollment_status', 'status'),
        Index('idx_enrollment_user', 'user_id'),
    )

    def to_dict(self, include_course=False):
        """
        Convert enrollment model to dictionary representation.
        
        Args:
            include_course (bool): Whether to include course information
        
        Returns:
            dict: Dictionary representation of the enrollment
        """
        data = {
            "id": str(self.id),
            "course_id": str(self.course_id),
            "student_id": str(self.student_id),
            "status": self.status.value if hasattr(self.status, 'value') else self.status,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "grade": self.grade,
            "progress": self.progress,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_favorited": self.is_favorited,
        }
        
        if include_course and self.course:
            data["course"] = {
                "id": str(self.course.id),
                "title": self.course.title,
                "code": self.course.code
            }
            
        return data

# Module Model (Course → Modules)
class Module(Base):
    __tablename__ = "module"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(UUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)  # e.g., "Week 1"
    position = Column(Integer, nullable=False)  # 1 week 1, 2 week 2
    course = relationship("Course", back_populates="modules")
    lectures = relationship("Lecture", back_populates="module", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("course_id", "position", name="module_position_unique"),
        Index('idx_module_course', 'course_id'),
    )

    def to_dict(self, include_lectures=False):
        """Convert module to dictionary with option to include lectures"""
        data = {
            "id": str(self.id),
            "course_id": str(self.course_id),
            "title": self.title,
            "position": self.position,
        }
        
        if include_lectures and self.lectures:
            data["lectures"] = [lecture.to_dict() for lecture in self.lectures]
            
        return data

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


class UserRecommendedCourses(Base):
    __tablename__ = "user_recommended_courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Links to the user
    title = Column(String, nullable=False)  # Course title
    type = Column(String, nullable=False)  # Course type
    progress = Column(Integer, default=0)  # Progress percentage
    thumbnail_path = Column(String, nullable=False, default="https://placehold.co/100x100")  # Default thumbnail
    reason = Column(Text, nullable=True)  # Recommendation reason
    tutorial_url = Column(String, nullable=False)  # for Tutorial type else Null
    
    # Relationships
    user = relationship("User", back_populates="recommended_courses")

    # Add index for user_id
    __table_args__ = (
        Index('idx_recommended_user', 'user_id'),
    )

    def to_dict(self):
        """Converts the UserRecommendedCourses object to a dictionary"""
        return {
            "id": self.id,
            "user_id": str(self.user_id),  # Convert UUID to string
            "title": self.title,
            "type": self.type,
            "progress": self.progress,
            "thumbnail_path": self.thumbnail_path,
            "reason": self.reason,
            "tutorial_url": self.tutorial_url
        }

class BookmarkedMaterials(Base):
    __tablename__ = "bookmarked_materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Links to the user
    title = Column(String, nullable=False)  # Material title
    type = Column(String, nullable=False)  # e.g., Article, Video, Course
    author = Column(String, nullable=True)  # Author name (optional)
    date_bookmarked = Column(DateTime, default=datetime.utcnow)  # Timestamp of bookmarking
    course_id = Column(UUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)  # Links to the course (optional)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    
    # Add indexes for frequent queries
    __table_args__ = (
        Index('idx_bookmarked_user', 'user_id'),
        Index('idx_bookmarked_course', 'course_id'),
        Index('idx_bookmarked_type', 'type'),
    )
    
    def to_dict(self):
        """Converts the BookmarkedMaterials object to a dictionary"""
        return {
            "id": self.id,
            "user_id": str(self.user_id),  # Convert UUID to string
            "title": self.title,
            "type": self.type,
            "author": self.author,
            "date_bookmarked": self.date_bookmarked.isoformat()  # Convert datetime to string
        }

# Initialize Database Tables
async def init_db():
    """Initialize the database tables asynchronously."""
    async with engine.begin() as conn:
        # Drop all tables first to ensure clean state
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
