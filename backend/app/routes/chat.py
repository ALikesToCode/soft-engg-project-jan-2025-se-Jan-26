from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import uuid

from app.database import get_db
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatSessionCreate, 
    ChatSessionUpdate, 
    ChatSession, 
    ChatMessageCreate, 
    ChatMessage, 
    ChatHistoryResponse
)
from app.services.auth_service import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.services.function_router import function_router
from langchain.schema import HumanMessage
from pydantic import BaseModel
from fastapi import Request

router = APIRouter()

# Request model for root chat endpoint
class ChatRequest(BaseModel):
    id: Optional[str] = None
    query: str
    context: Optional[Dict[str, Any]] = None
    function_results: Optional[List[Dict[str, Any]]] = None

# Response model for root chat endpoint
class ChatResponse(BaseModel):
    content: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    function_results: Optional[List[Dict[str, Any]]] = None

@router.post("/sessions", response_model=ChatSession, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session"""
    # If user is authenticated, associate the session with them
    if current_user:
        session_data.user_id = current_user.id
    
    chat_session = await ChatService.create_session(db, session_data)
    return chat_session

@router.get("/sessions", response_model=ChatHistoryResponse)
async def get_user_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    sessions = await ChatService.get_sessions_by_user(db, current_user.id)
    return ChatHistoryResponse(sessions=sessions)

@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a chat session by ID"""
    chat_session = await ChatService.get_session_by_id(db, session_id)
    
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # If the session belongs to a user, verify ownership
    if chat_session.user_id and current_user:
        if chat_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this chat session"
            )
    
    return chat_session

@router.put("/sessions/{session_id}", response_model=ChatSession)
async def update_chat_session(
    session_id: str,
    session_data: ChatSessionUpdate,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a chat session"""
    # First get the session to verify ownership
    existing_session = await ChatService.get_session_by_id(db, session_id)
    
    if not existing_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # If the session belongs to a user, verify ownership
    if existing_session.user_id and current_user:
        if existing_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this chat session"
            )
    
    updated_session = await ChatService.update_session(db, session_id, session_data)
    return updated_session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat session"""
    # First get the session to verify ownership
    existing_session = await ChatService.get_session_by_id(db, session_id)
    
    if not existing_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # If the session belongs to a user, verify ownership
    if existing_session.user_id and current_user:
        if existing_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this chat session"
            )
    
    deleted = await ChatService.delete_session(db, session_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )

@router.post("/sessions/{session_id}/messages", response_model=ChatMessage)
async def add_message(
    session_id: str,
    message_data: ChatMessageCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a message to a chat session"""
    # First get the session to verify ownership
    existing_session = await ChatService.get_session_by_id(db, session_id)
    
    if not existing_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # If the session belongs to a user, verify ownership
    if existing_session.user_id and current_user:
        if existing_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add messages to this chat session"
            )
    
    message = await ChatService.add_message(db, session_id, message_data)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message"
        )
    
    return message

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_messages(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a chat session"""
    # First get the session to verify ownership
    existing_session = await ChatService.get_session_by_id(db, session_id)
    
    if not existing_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # If the session belongs to a user, verify ownership
    if existing_session.user_id and current_user:
        if existing_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view messages for this chat session"
            )
    
    messages = await ChatService.get_messages(db, session_id)
    return messages

@router.get("/available-functions", response_model=List[Dict[str, Any]])
async def get_available_functions(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    Get all available functions that the AI assistant can call
    
    This endpoint returns a list of function declarations that the frontend can use
    to display available API functionality to users or to the AI model.
    Functions are filtered based on user role permissions.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Getting available functions")
        
        # Get all function declarations from the function router
        function_declarations = function_router.get_function_declarations()
        logger.info(f"Retrieved {len(function_declarations)} function declarations")
        
        # If no functions are registered, provide default ones
        if not function_declarations:
            logger.warning("No function declarations found, using default functions")
            function_declarations = [
                {
                    "name": "web_search",
                    "description": "Search the web for current information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "getCourses",
                    "description": "Get all available courses for the current user",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "getCourseById",
                    "description": "Get details of a specific course by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "courseId": {
                                "type": "string",
                                "description": "The ID of the course to retrieve"
                            }
                        },
                        "required": ["courseId"]
                    }
                }
            ]
            logger.info(f"Added {len(function_declarations)} default functions")
        
        # Filter functions based on user role
        user_role = "anonymous"
        if current_user:
            # Extract role from user dict - current_user is now a dict not a User model
            user_role = current_user.get("role", "anonymous").lower()
            logger.info(f"User authenticated with role: {user_role}")
        else:
            logger.info("No authenticated user, using anonymous role")
        
        # Define role-based function access
        role_permissions = {
            "admin": set([  # Admins can access all functions
                "getCourses", "getCourseById", "getAssignments", "getUserProfile",
                "getQuizzes", "getSubmissions", "web_search", "get_user_info",
                "get_user_course_history", "get_course_enrollment", "get_course_assignments",
                "search_faqs", "get_faq_categories", "get_system_settings", 
                "get_assignment_details", "get_system_health", "get_system_metrics",
                "query_course_materials"
            ]),
            "faculty": set([  # Faculty can access most functions but not admin ones
                "getCourses", "getCourseById", "getAssignments", "getUserProfile",
                "getQuizzes", "getSubmissions", "web_search", "get_user_info",
                "get_user_course_history", "get_course_enrollment", "get_course_assignments",
                "search_faqs", "get_faq_categories", "get_assignment_details",
                "query_course_materials"
            ]),
            "student": set([  # Students have limited access
                "getCourses", "getCourseById", "getAssignments", "getUserProfile",
                "getQuizzes", "web_search", "get_user_info", "get_user_course_history",
                "search_faqs", "get_faq_categories", "get_assignment_details",
                "query_course_materials"
            ]),
            "anonymous": set([  # Unauthenticated users have minimal access
                "web_search", "search_faqs", "get_faq_categories"
            ])
        }
        
        # Default to anonymous permissions if role not found
        allowed_functions = role_permissions.get(user_role, role_permissions["anonymous"])
        logger.info(f"User has access to {len(allowed_functions)} functions")
        
        # Filter declarations and format for frontend
        formatted_functions = []
        for func in function_declarations:
            # Check if function has a valid name field
            if "name" not in func:
                logger.warning(f"Function declaration missing name field: {func}")
                continue
                
            # Check if the function is allowed for this user role
            if func["name"] in allowed_functions:
                try:
                    formatted_functions.append({
                        "name": func["name"],
                        "description": func.get("description", ""),
                        "parameters": func.get("parameters", {})
                    })
                except Exception as format_error:
                    logger.error(f"Error formatting function {func['name']}: {str(format_error)}")
        
        logger.info(f"Returning {len(formatted_functions)} filtered functions")
        return formatted_functions
    except Exception as e:
        logger.error(f"Error getting available functions: {str(e)}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting available functions: {str(e)}"
        ) 

@router.post("/", response_model=ChatResponse)
async def process_chat(
    request: ChatRequest,
    req: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process a chat message and return a response
    This endpoint is a proxy to the LLM service for compatibility with the frontend
    """
    try:
        # Forward the request to the LLM service
        from app.routes.llm import chat as llm_chat
        
        # Create a LLMRequest for the llm_chat function
        from app.routes.llm import LLMRequest
        llm_request = LLMRequest(
            id=request.id or str(uuid.uuid4()),
            query=request.query
        )
        
        # Call the LLM chat function
        result = await llm_chat(llm_request, req, current_user)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {str(e)}"
        )

@router.get("/", response_model=Dict[str, Any])
async def get_chat_history(
    id: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat history for a specific thread or all chat sessions
    """
    try:
        if id:
            # Get messages for a specific session
            session = await ChatService.get_session_by_id(db, id)
            if not session:
                return {"messages": []}
                
            messages = await ChatService.get_messages(db, id)
            return {"messages": messages}
        else:
            # Get all sessions
            if not current_user:
                return {"sessions": []}
                
            sessions = await ChatService.get_sessions_by_user(db, current_user.id)
            return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )

@router.delete("/", status_code=status.HTTP_200_OK)
async def clear_chat(
    id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear chat history for a specific thread
    """
    try:
        # Check if session exists
        session = await ChatService.get_session_by_id(db, id)
        if not session:
            return {"success": True, "message": "Chat session not found or already deleted"}
            
        # Delete the session
        await ChatService.delete_session(db, id)
        return {"success": True, "message": "Chat session cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear chat: {str(e)}"
        ) 