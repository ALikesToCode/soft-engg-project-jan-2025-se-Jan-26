from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class ChatMessageBase(BaseModel):
    """Base schema for chat messages"""
    content: str
    type: str = Field(..., description="Message type: 'user' or 'ai'")
    function_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Any function calls made by the AI")

class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message"""
    pass

class ChatMessage(ChatMessageBase):
    """Schema for a chat message with database fields"""
    id: int
    chat_session_id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True

class ChatSessionBase(BaseModel):
    """Base schema for chat sessions"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a new chat session"""
    user_id: Optional[int] = None

class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session"""
    title: Optional[str] = None

class ChatSession(ChatSessionBase):
    """Schema for a chat session with database fields"""
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []
    
    class Config:
        orm_mode = True

class ChatHistoryResponse(BaseModel):
    """Schema for returning a chat history response"""
    sessions: List[ChatSession]
    
    class Config:
        orm_mode = True 