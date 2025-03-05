from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Dict


router = APIRouter(prefix="/notification")

class NotificationMessage(BaseModel):
    user_id: str
    message: str
    type: str  # "websocket", "email", "push"

class NotificationPreferences(BaseModel):
    email_enabled: bool
    push_enabled: bool
    websocket_enabled: bool

@router.get("/")
async def get_notifications(user_id: int):
    return {"user_id": user_id, "notifications": ["Notification 1", "Notification 2"]}

user_preferences: Dict[int, Dict] = {}

@router.put("/preferences")
async def update_preferences(user_id: str, preferences: NotificationPreferences):
    user_preferences[user_id] = preferences.dict()
    return JSONResponse(content={"message": "Preferences updated", "preferences": user_preferences[user_id]})

@router.post("/send",
             name="Send Notification",
             description="Sends Notifications to opted users")
async def notify():
    pass
