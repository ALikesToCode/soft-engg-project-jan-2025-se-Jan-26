from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Dict
from app.services.auth_service import oauth2_scheme, get_current_user


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
async def get_notifications(user_id: int, current_user: dict = Depends(get_current_user)):
    return {"user_id": user_id, "notifications": ["Notification 1", "Notification 2"]}

user_preferences: Dict[int, Dict] = {}

@router.put("/preferences")
async def update_preferences(user_id: str, preferences: NotificationPreferences, current_user: dict = Depends(get_current_user)):
    user_preferences[user_id] = preferences.dict()
    return JSONResponse(content={"message": "Preferences updated", "preferences": user_preferences[user_id]})

@router.post("/send",
             name="Send Notification",
             description="Sends Notifications to opted users")
async def notify(current_user: dict = Depends(get_current_user)):
    pass
