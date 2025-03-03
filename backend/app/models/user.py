from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base, engine
from app.models.course import user_courses  # Import junction table
from app.models.role import user_roles  # Import junction table
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    courses = relationship("Course", secondary=user_courses, back_populates="users")  # Many-to-Many with Course
    roles = relationship("Role", secondary=user_roles, back_populates="users")  # Many-to-Many with Role

    def __repr__(self):
        return f"<User(email={self.email}, roles={[role.name for role in self.roles]}, courses={[course.title for course in self.courses]})>"

# Create the table in the database
async def init_db():
    """Initialize the database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
