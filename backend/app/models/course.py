from sqlalchemy import Column, String, Integer, \
    DateTime, ForeignKey, Text, Table, UniqueConstraint, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base, engine
from datetime import datetime

# Many-to-Many: Users & Courses
user_courses = Table(
    "user_courses",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", Integer, ForeignKey("course.id", ondelete="CASCADE"), primary_key=True)
)

# Course Model
class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    syllabus = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    credits = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)  # e.g., Weeks or Months
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", secondary=user_courses, back_populates="courses")  # Many-to-Many with Users
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")  # One-to-Many

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "syllabus": self.syllabus,
            "description": self.description,
            "credits": self.credits,
            "duration": self.duration,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            # "users": [user.id for user in self.users]  # Only storing user IDs
        }

# Module Model (Course → Modules)
class Module(Base):
    __tablename__ = "module"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
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
    content_doc = Column(LargeBinary, nullable=False)  # Stores actual file content (PDF, DOC, PPT, PPTX)
    file_type = Column(String, nullable=False)  # Stores MIME type (e.g., application/pdf, application/vnd.ms-powerpoint)

    lecture = relationship("Lecture", back_populates="contents_doc")

    def to_dict(self):
        return {
            "id": str(self.id),
            "lecture_id": str(self.lecture_id),
            "lecture_title": self.title,
            "file_name": self.file_name,  # Returning file name instead of binary content
            "file_type": self.file_type,
            "content_desc": self.content_desc,
        }



# Initialize Database Tables
async def init_db():
    """Initialize the database tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
