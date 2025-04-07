import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Index, types
from sqlalchemy.orm import relationship
from app.database import Base, engine, UUID
from app.models.course import Course, user_courses
from app.models.role import Role, user_roles
from datetime import datetime, UTC
import enum
from sqlalchemy.dialects.postgresql import ENUM
from typing import Optional, Dict, Any

# Create a custom SQLAlchemy type for case-insensitive enums
class CaseInsensitiveEnumType(types.TypeDecorator):
    """
    Custom SQLAlchemy type that handles case-insensitive enum values.
    Converts values from the database to the proper enum value regardless of case.
    """
    impl = types.String
    cache_ok = True

    def __init__(self, enum_class):
        super(CaseInsensitiveEnumType, self).__init__()
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        
        # Handle case-insensitive lookup
        if isinstance(value, str):
            upper_value = value.upper()
            for member in self.enum_class:
                if member.value.upper() == upper_value:
                    return member
        
        # If not found by case-insensitive lookup, try to get it directly
        try:
            return self.enum_class(value)
        except ValueError:
            # Return the enum's default value if no match is found
            return self.enum_class.STUDENT

# Define User Role as String-based Enum for compatibility
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    FACULTY = "FACULTY"
    STUDENT = "STUDENT"
    
    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive lookup of enum values."""
        if isinstance(value, str):
            # Convert input to uppercase for matching
            upper_value = value.upper()
            for member in cls:
                if member.value.upper() == upper_value:
                    return member
        return None

# Association table for many-to-many relationship between users and courses
# Removed duplicate definition of user_courses as it's now imported from course.py

class User(Base):
    """
    User model representing system users including students, faculty, and administrators.
    
    This model stores authentication information, profile details, and relationships
    to courses and other entities in the system.
    
    Attributes:
        id: Unique UUID primary key for the user
        email: User's email address (used for login)
        name: User's display name
        hashed_password: Securely hashed password
        role: User role (ADMIN, FACULTY, or STUDENT)
        is_google_user: Whether the user is a Google user
        picture: User's profile picture URL
        created_at: Timestamp when the user record was created
        updated_at: Timestamp when the user record was last updated
    """
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    # Use custom type instead of ENUM for case-insensitive handling
    role = Column(CaseInsensitiveEnumType(UserRole), nullable=False, default=UserRole.STUDENT)
    is_google_user = Column(Boolean, nullable=False, default=False)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    courses = relationship("Course", secondary=user_courses, back_populates="users")
    courses_taught = relationship("Course", foreign_keys="Course.faculty_id", back_populates="faculty")
    course_enrollments = relationship("CourseEnrollment", foreign_keys="CourseEnrollment.student_id", back_populates="student")
    enrollments = relationship("CourseEnrollment", foreign_keys="CourseEnrollment.user_id", back_populates="user")
    recommended_courses = relationship("UserRecommendedCourses", back_populates="user")
    bookmarks = relationship("BookmarkedMaterials", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    # Add indexes for frequently queried fields
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_role', 'role'),
        Index('idx_user_role_created', 'role', 'created_at'),
    )

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert user model to dictionary representation.
        
        Args:
            include_sensitive: Whether to include sensitive fields like hashed_password
        
        Returns:
            Dictionary representation of the user
        """
        data = {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "role": self.role.value if hasattr(self.role, 'value') else self.role,
            "is_google_user": self.is_google_user,
            "picture": self.picture,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Include sensitive fields only when explicitly requested
        if include_sensitive:
            data["hashed_password"] = self.hashed_password
            
        return data

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
