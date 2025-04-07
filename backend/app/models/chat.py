from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean, MetaData
from sqlalchemy.orm import relationship
from app.database import Base, UUID
import datetime

class ChatSession(Base):
    """Model for storing chat sessions"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True)  # Client-side generated UUID
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)  # Can be anonymous
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="chat_sessions")
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Model for storing chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    type = Column(String(10), nullable=False)  # 'user' or 'ai'
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Additional metadata
    function_calls = Column(Text, nullable=True)  # JSON string of function calls
    
    # Relationship to chat session
    chat_session = relationship("ChatSession", back_populates="messages") 