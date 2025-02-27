from fastapi import APIRouter
from pydantic import BaseModel

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
    query:str

router = APIRouter()
@router.post("/chat")
async def chat(request: LLMRequest):
    chat_history.append(HumanMessage(request.query))
    ai_response = llm.invoke(chat_history).content
    chat_history.append(AIMessage(ai_response))

    return ai_response

@router.get("/chat")
async def get_chat_history():
    return chat_history