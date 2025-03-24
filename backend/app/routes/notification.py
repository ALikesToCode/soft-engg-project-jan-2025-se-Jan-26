from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, UUID4
from fastapi.responses import JSONResponse
from typing import Dict
from datetime import datetime
from typing import Optional
from app.services.auth_service import oauth2_scheme, get_current_user, require_auth
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notification")

# Course Notification Schema
class CourseNotification(BaseModel):
    type: str = "course"
    priority: str
    category: str
    title: str
    message: str
    courseId: UUID4

    class Config:
        orm_mode = True

# System Notification Schema
class SystemNotification(BaseModel):
    type: str = "system"
    priority: str
    category: str
    title: str
    message: str

    class Config:
        orm_mode = True

# User Notification Status Schema
class UserNotificationStatus(BaseModel):
    id: int
    user_id: int
    notification_id: int
    read: bool

    class Config:
        orm_mode = True

class NotificationPreferences(BaseModel):
    email_enabled: bool
    push_enabled: bool
    websocket_enabled: bool

@router.get("/")
async def get_notifications(
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(require_auth),
):
    user_id = current_user['sub']
    try:
        notifications = await NotificationService.get_user_notification(db, user_id)
        return notifications
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
user_preferences: Dict[int, Dict] = {}

@router.put("/preferences")
async def update_preferences(user_id: str, preferences: NotificationPreferences, current_user: dict = Depends(get_current_user)):
    user_preferences[user_id] = preferences.dict()
    return JSONResponse(content={"message": "Preferences updated", "preferences": user_preferences[user_id]})

@router.post("/course/send",
             name="Send Course Notification",
             description="Sends Notifications to opted users")
async def send_course_notification(
    notification_content: CourseNotification,
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(require_auth)):
    user_id = current_user['sub']
    try:
        logger.info("Going to save the notification to be sent")
        notification = await NotificationService.save_course_notification(notification_content, db, user_id)
        return notification
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/send",
             name="Send System Notification",
             description="Sends Notifications to opted users")
async def notify(sys_notification_content: SystemNotification, 
                 db: AsyncSession = Depends(get_db), 
                 current_user: dict = Depends(require_auth)):
    user_id = current_user['sub']
    try:
        logger.info("Going to save the system notification to be sent")
        notification = await NotificationService.save_system_notification(sys_notification_content, db, user_id)
        return notification
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


