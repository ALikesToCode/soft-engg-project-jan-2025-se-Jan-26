import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Table, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base, engine, UUID
from app.models.course import Course, user_courses
from app.models.role import Role, user_roles
from datetime import datetime, UTC

class User(Base):
    """
    User model representing application users.
    
    This model stores essential user information including authentication details,
    profile data, and role assignments. It supports both traditional email/password
    authentication and Google OAuth authentication.
    
    The model includes timestamps for creation and updates, allowing for audit trails
    and data lifecycle management.
    
    Attributes:
        id: Unique UUID primary key for the user
        email: User's email address (unique, indexed)
        name: User's display name
        hashed_password: Bcrypt-hashed password (nullable for Google users)
        is_google_user: Flag indicating if the user authenticated via Google
        picture: URL to the user's profile picture
        created_at: Timestamp when the user record was created
        updated_at: Timestamp when the user record was last updated
        role: User's role in the system (student, faculty, or support)
        courses_taught: List of courses taught by the user (faculty only)
        course_enrollments: List of course enrollments (student only)
    """
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4, 
                comment="Unique identifier for the user")
    email = Column(String, unique=True, index=True, 
                  comment="User's email address, used for authentication and communication")
    name = Column(String, 
                 comment="User's display name", default="User Name")
    hashed_password = Column(String, nullable=True, 
                            comment="Bcrypt-hashed password, nullable for Google OAuth users")
    is_google_user = Column(Boolean, default=False, 
                           comment="Flag indicating if the user authenticated via Google OAuth")
    picture = Column(String, nullable=True, 
                    comment="URL to the user's profile picture, typically from Google profile")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), 
                       comment="Timestamp when the user record was created")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), 
                       comment="Timestamp when the user record was last updated")
    # three roles are defined: student, faculty, support
    role = Column(String, default="student", 
                 comment="User's role in the system: student, faculty, or support")

    # Course relationships
    courses = relationship("Course", secondary=user_courses, back_populates="users")  # Many-to-Many with Course
    roles = relationship("Role", secondary=user_roles, back_populates="users")  # Many-to-Many with Role
    courses_taught = relationship("Course", foreign_keys="[Course.faculty_id]", back_populates="faculty")
    
    # Updated relationships
    enrollments = relationship("CourseEnrollment", foreign_keys="[CourseEnrollment.user_id]", back_populates="user")  # One-to-Many with CourseEnrollment
    course_enrollments = relationship("CourseEnrollment", foreign_keys="[CourseEnrollment.student_id]", back_populates="student")  # One-to-Many with CourseEnrollment
    bookmarks = relationship("BookmarkedMaterials", back_populates="user")  # One-to-Many with BookmarkedMaterials
    recommended_courses = relationship("UserRecommendedCourses", back_populates="user")  # One-to-Many with UserRecommendedCourses
    
    # Chat relationship
    chat_sessions = relationship("ChatSession", back_populates="user")  # One-to-Many with ChatSession

# Create the table in the database
async def init_db():
    """
    Initialize the database tables.
    
    This function creates all tables defined in the models if they don't already exist.
    It should be called during application startup to ensure the database schema is properly set up.
    
    Returns:
        None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
