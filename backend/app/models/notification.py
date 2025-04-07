from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from app.database import Base, engine, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Course Notification Model
class CourseNotification(Base):
    __tablename__ = "course_notification"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String, default="course", nullable=False)
    priority = Column(String, nullable=False)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    course_id = Column(UUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    sent_by = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "priority": self.priority,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "course_id": str(self.course_id),
            "user_id": str(self.sent_by),
        }

# System Notification Model
class SystemNotification(Base):
    __tablename__ = "system_notification"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String, default="system", nullable=False)
    priority = Column(String, nullable=False)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    sent_by = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "priority": self.priority,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "user_id": str(self.sent_by),
        }

# User Notification Status Model
class UserNotificationStatus(Base):
    __tablename__ = "user_notification_status"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False, default='course')
    read = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": str(self.user_id),
            "notification_id": self.notification_id,
            "read": self.read,
        }

# Initialize Database Tables
async def init_db():
    """Initialize the database tables asynchronously."""
    async with engine.begin() as conn:
        # Drop all tables first to ensure clean state
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)