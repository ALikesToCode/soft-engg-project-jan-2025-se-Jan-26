from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, UUID4
from fastapi.responses import JSONResponse
from typing import Dict, List
from datetime import datetime
from typing import Optional
from app.services.auth_service import oauth2_scheme, get_current_user, require_auth
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Course Notification Schema
class CourseNotification(BaseModel):
    type: str = "course"
    priority: str
    category: str
    title: str
    message: str
    courseId: UUID4
    timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True

# System Notification Schema
class SystemNotification(BaseModel):
    type: str = "system"
    priority: str
    category: str
    title: str
    message: str
    timestamp: Optional[datetime] = None

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
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/recent-notifications')
async def get_recent_notifications_for_faculty_or_support(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    user_id = current_user["sub"]
    try:
        recent_notifications = await NotificationService.get_recent_notifications_for_faculty_or_support(db, user_id)
        return recent_notifications
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail="Could not get recent notifications")
    
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
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as http_ex:
        raise http_ex
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
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put('/{type}/{id}')
async def markNotificationAsRead(
    type: str,
    id: int,
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(require_auth)
):
    user_id = current_user['sub']
    try:
        notification = await NotificationService.markNotificationAsRead(id,type, db, user_id)
        return notification
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class NotificationReadRequest(BaseModel):
    notifications: List[dict]  # Expecting a list of {"id": <id>, "type": <type>}


@router.put('/mark-all')
async def markAllNotificationAsRead(
    request:NotificationReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    user_id = current_user["sub"]
    try:
        updated_notifications = await NotificationService.markAllNotificationAsRead(request.notifications, db, user_id)
        return {"success": True, "updated_notifications": updated_notifications}
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail="Could not update notifications")
    

@router.delete('/delete/{type}/{id}')
async def markNotificationAsRead(
    type: str,
    id: int,
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(require_auth)
):
    user_id = current_user["sub"]
    _id = id
    try:
        deleted_notifications = await NotificationService.delete_notification_by_id(_id, type, db, user_id)
        return {"success": True, "deleted_notifications": deleted_notifications}
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail="Could not update notifications")
    
    


