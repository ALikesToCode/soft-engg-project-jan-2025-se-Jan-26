from fastapi import APIRouter
from pydantic import BaseModel

class LLMRequest(BaseModel):
    query:str

router = APIRouter()
@router.post("/chat")
async def chat(request: LLMRequest):
    return f"llm.py():/chat: request:{request}"