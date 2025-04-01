from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate, ChatSessionUpdate

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat-related operations"""
    
    @staticmethod
    async def create_session(db: AsyncSession, session_data: ChatSessionCreate) -> ChatSession:
        """Create a new chat session"""
        chat_session = ChatSession(
            session_id=session_data.session_id,
            user_id=session_data.user_id,
            title=session_data.title
        )
        db.add(chat_session)
        await db.commit()
        await db.refresh(chat_session)
        return chat_session
    
    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by its session_id"""
        query = select(ChatSession).where(ChatSession.session_id == session_id)
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def get_sessions_by_user(db: AsyncSession, user_id: int) -> List[ChatSession]:
        """Get all chat sessions for a user"""
        query = select(ChatSession).where(ChatSession.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_session(db: AsyncSession, session_id: str, session_data: ChatSessionUpdate) -> Optional[ChatSession]:
        """Update a chat session"""
        # Get the session first
        session = await ChatService.get_session_by_id(db, session_id)
        if not session:
            return None
        
        # Update the session
        if session_data.title is not None:
            session.title = session_data.title
        
        session.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(session)
        return session
    
    @staticmethod
    async def delete_session(db: AsyncSession, session_id: str) -> bool:
        """Delete a chat session"""
        session = await ChatService.get_session_by_id(db, session_id)
        if not session:
            return False
        
        await db.delete(session)
        await db.commit()
        return True
    
    @staticmethod
    async def add_message(db: AsyncSession, session_id: str, message_data: ChatMessageCreate) -> Optional[ChatMessage]:
        """Add a message to a chat session"""
        # Get the session first
        session = await ChatService.get_session_by_id(db, session_id)
        if not session:
            return None
        
        # Create the message
        function_calls_json = None
        if message_data.function_calls:
            try:
                function_calls_json = json.dumps(message_data.function_calls)
            except Exception as e:
                logger.error(f"Error serializing function calls: {str(e)}")
        
        chat_message = ChatMessage(
            chat_session_id=session.id,
            content=message_data.content,
            type=message_data.type,
            function_calls=function_calls_json
        )
        
        db.add(chat_message)
        
        # Update the session's updated_at timestamp
        session.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(chat_message)
        return chat_message
    
    @staticmethod
    async def get_messages(db: AsyncSession, session_id: str) -> List[ChatMessage]:
        """Get all messages for a chat session"""
        session = await ChatService.get_session_by_id(db, session_id)
        if not session:
            return []
        
        query = select(ChatMessage).where(ChatMessage.chat_session_id == session.id).order_by(ChatMessage.timestamp)
        result = await db.execute(query)
        return result.scalars().all() 