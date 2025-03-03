from fastapi import APIRouter
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

chat_history = []

async def startNewChat():
    chat_history = []
    return True

class LLMRequest(BaseModel):
    """
    Schema for chat requests.
    
    Attributes:
        query: The user's message to send to the AI
    """
    query: str = Field(..., description="The user's message to the AI", example="What courses are available in the IITM program?")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What courses are available in the IITM program?"
            }
        }

router = APIRouter()

@router.post("/chat", 
    summary="Send message to AI",
    description="Sends a message to the AI and returns the AI's response",
    response_description="AI's response to the user's message",
    responses={
        200: {
            "description": "AI response generated successfully",
            "content": {
                "application/json": {
                    "example": "There are several courses available in the IITM program, including Data Structures and Algorithms, Machine Learning, and Database Systems."
                }
            }
        },
        500: {
            "description": "Server error during AI processing",
            "content": {
                "application/json": {
                    "example": {"detail": "Error generating AI response"}
                }
            }
        }
    }
)
async def chat(request: LLMRequest):
    """
    Send a message to the AI and get a response.
    
    This endpoint processes the user's message using the Gemini AI model
    and returns the AI's response. The conversation history is maintained
    for context.
    
    Args:
        request: The LLMRequest containing the user's message
        
    Returns:
        The AI's response as a string
    """
    chat_history.append(HumanMessage(request.query))
    ai_response = llm.invoke(chat_history).content
    chat_history.append(AIMessage(ai_response))

    return ai_response

@router.get("/chat", 
    summary="Get chat history",
    description="Retrieves the current conversation history with the AI",
    response_description="List of messages in the conversation",
    responses={
        200: {
            "description": "Chat history retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {"type": "human", "content": "What courses are available in the IITM program?"},
                        {"type": "ai", "content": "There are several courses available in the IITM program, including Data Structures and Algorithms, Machine Learning, and Database Systems."}
                    ]
                }
            }
        }
    }
)
async def get_chat_history():
    """
    Get the current conversation history with the AI.
    
    This endpoint returns the complete history of the current conversation,
    including both user messages and AI responses.
    
    Returns:
        List of messages in the conversation
    """
    return chat_history