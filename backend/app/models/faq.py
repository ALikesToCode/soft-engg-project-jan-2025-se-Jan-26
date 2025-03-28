from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid

from app.database import Base, UUID


class FAQ(Base):
    """FAQ model for storing frequently asked questions and answers."""
    
    __tablename__ = "faqs"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    category_id = Column(String(50), nullable=False, default='general')  # general, technical, courses, account, faculty
    priority = Column(Integer, default=0)  # Higher numbers appear first
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FAQ(id={self.id}, question={self.question[:30]}...)>" 