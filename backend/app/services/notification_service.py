from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import CourseNotification, SystemNotification ,UserNotificationStatus
from app.models.course import CourseEnrollment
from app.models.user import User
from app.validators.notification_validator import NotificationValidator
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy import select, and_
from typing import List, Dict
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class NotificationService:

    @staticmethod
    async def get_user_notification(db: AsyncSession, user_id: UUID):
        logger.info("Just entered in get_user_notification in NotificationService class")
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        logger.info(f"User found with id = {user_id} and role = {user.role}")
        try:

            if user.role.lower() in ['faculty', 'support']:
                # list of notifications for faculty or support users
                notifications = await NotificationService.get_recent_notifications_for_faculty_or_support(db, user_id)
                response = []
                for notif in notifications:
                    logger.info(f"notification ===== {notif}")
                    response.append({
                        "user_id": notif["user_id"],
                        "notification_id": notif["id"],
                        "read": False,
                        "notification_type": notif["type"],
                        "priority": notif["priority"],
                        "category": notif["category"],
                        "title": notif["title"],
                        "message": notif["message"],
                        "timestamp": notif["timestamp"],
                        "course_id": notif.get("course_id")
                    })
                logger.info(f"{user.role} Notification fetched successfully...")
                return response

            # Fetch user notifications
            result = await db.execute(select(UserNotificationStatus).where(UserNotificationStatus.user_id == user_id))
            user_notifications = result.scalars().all()
            notifications = []

            for user_notification in user_notifications:
                # Fetch CourseNotification
                course_notif_result = await db.execute(
                    select(CourseNotification).where(CourseNotification.id == user_notification.notification_id)
                )
                course_notif = course_notif_result.scalars().first()

                if course_notif:
                    notifications.append({
                        "user_id": user_notification.user_id,
                        "notification_id": user_notification.notification_id,
                        "read": user_notification.read,
                        "notification_type": course_notif.type,
                        "priority": course_notif.priority,
                        "category": course_notif.category,
                        "title": course_notif.title,
                        "message": course_notif.message,
                        "timestamp": course_notif.timestamp,
                        "course_id": course_notif.course_id,
                    })
                    # Skip system notification check if course notification is found
                    continue
                
                # Fetch SystemNotification
                system_notif_result = await db.execute(
                    select(SystemNotification).where(SystemNotification.id == user_notification.notification_id)
                )
                system_notif = system_notif_result.scalars().first()

                if system_notif:
                    notifications.append({
                        "user_id": user_notification.user_id,
                        "notification_id": user_notification.notification_id,
                        "read": user_notification.read,
                        "notification_type": system_notif.type,
                        "priority": system_notif.priority,
                        "category": system_notif.category,
                        "title": system_notif.title,
                        "message": system_notif.message,
                        "timestamp": system_notif.timestamp,
                        "course_id": None,  # System notifications don't have a course_id
                    })

            logger.info("User Notification fetched successfully...")
            return notifications

        except Exception as e:
            logger.error(f"Error fetching notification: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_recent_notifications_for_faculty_or_support(db: AsyncSession, user_id: UUID):
        logger.info("Just entered in get_recent_notifications_for_faculty_or_support in NotificationService class")
        try:
            # Fetch recent course notifications sent by the user
            course_result = await db.execute(
                select(CourseNotification)
                .where(CourseNotification.sent_by == user_id)
                .order_by(CourseNotification.timestamp.desc())
            )
            course_notifications = course_result.scalars().all()

            # Fetch recent system notifications sent by the user
            system_result = await db.execute(
                select(SystemNotification)
                .where(SystemNotification.sent_by == user_id)
                .order_by(SystemNotification.timestamp.desc())
            )
            system_notifications = system_result.scalars().all()

            # Combine and format notifications
            notifications = []
            
            for notif in course_notifications + system_notifications:
                notif_dict = notif.to_dict()
                notif_dict["timestamp"] = notif.timestamp.isoformat()
                notifications.append(notif_dict)

            logger.info("Successfully fetched %d notifications", len(notifications))

            return notifications

        except Exception as e:
            await db.rollback()
            logger.error(f"Error getting recent notifications: {str(e)}")
            raise HTTPException(status_code=500, detail="Could not fetch recent notifications")


    @staticmethod
    async def save_course_notification(notification_content,db: AsyncSession,user_id:UUID):
        logger.info("Just entered in save_course_notification in NotificationService class")

        #Validate the input data
        try:
            logger.info("Going to validate the input data")
            if not isinstance(notification_content, dict):
                __notification_content = notification_content.__dict__  # Convert to dict if it's an object

            validated_data = NotificationValidator.validate_course_notification(__notification_content)
            logger.info(f"Validation successful: {validated_data}")
        except ValueError as ve:
            logger.info(f"Validation failed {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))  # Return 400 Bad Request if validation fails

        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['faculty', 'support']:
            logger.info(f"You do not have permission to send this notification")
            raise HTTPException(status_code=403, detail="You are forbidden to user the resource")
        try:
            # Use the timestamp from notification_content if available, otherwise use current UTC time
            timestamp = getattr(notification_content, 'timestamp', None) or datetime.utcnow()
            
            notification = CourseNotification(
                type=notification_content.type,
                priority=notification_content.priority,
                category=notification_content.category,
                title=notification_content.title,
                message=notification_content.message,
                timestamp=timestamp,
                course_id=notification_content.courseId,
                sent_by = user_id
            )
            logger.info("Going to insert in CourseNotification table")
            db.add(notification)
            await db.flush()  

            logger.info(f"Now going to insert in UserNotificationStatus for all students in that course {notification.course_id}")
            result = await db.execute(select(CourseEnrollment).where(CourseEnrollment.course_id == notification.course_id))
            students = result.scalars().all()
            
            user_notifications = [
                UserNotificationStatus(
                    user_id=student.student_id,
                    notification_id=notification.id,
                    read=False
                    )
                for student in students
            ]

            db.add_all(user_notifications)
            await db.commit()
            logger.info("Data Saved successfully...")
            return notification.to_dict()
        except Exception as e:
            await db.rollback() 
            logger.error(f"Error saving notification: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def save_system_notification(sys_notification_content,db: AsyncSession,user_id:UUID):
        logger.info("In save_system_notification in NotificationService class")
        
        #Validate the input data
        try:
            logger.info("Going to validate the input data")
            if not isinstance(sys_notification_content, dict):
                __sys_notification_content = sys_notification_content.__dict__  # Convert to dict if it's an object

            validated_data = NotificationValidator.validate_system_notification(__sys_notification_content)
            logger.info(f"Sys notification Validation successful: {validated_data}")
        except ValueError as ve:
            logger.info(f"Sys notification Validation failed {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))  
        
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['support']:
            logger.info(f"You do not have permission to send this notification")
            raise HTTPException(status_code=403, detail="You are forbidden to user the resource")
        try:
            # Use the timestamp from sys_notification_content if available, otherwise use current UTC time
            timestamp = getattr(sys_notification_content, 'timestamp', None) or datetime.utcnow()
            
            sys_notification = SystemNotification(
                type=sys_notification_content.type,
                priority=sys_notification_content.priority,
                category=sys_notification_content.category,
                title=sys_notification_content.title,
                message=sys_notification_content.message,
                timestamp=timestamp,
                sent_by = user_id
            )
            logger.info("Going to insert in SystemNotification table")
            db.add(sys_notification)
            await db.flush()  

            logger.info(f"Now going to insert in UserNotificationStatus for all students")
            result = await db.execute(select(CourseEnrollment))
            students = result.scalars().all()
            
            user_notifications = [
                UserNotificationStatus(
                    user_id=student.student_id,
                    notification_id=sys_notification.id,
                    read=False
                    )
                for student in students
            ]

            db.add_all(user_notifications)
            await db.commit()
            logger.info("Data Saved successfully...")
            return sys_notification.to_dict()

        except Exception as e:
            await db.rollback() 
            logger.error(f"Error saving notification: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def markNotificationAsRead(notification_id: int, type:str, db: AsyncSession,user_id:UUID):
        logger.info(f"In markNotificationAsRead in NotificationService class with id = {notification_id}, type={type}")
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() in ['faculty', 'support']:
            logger.info(f"For faculty this feature is not available")
            raise HTTPException(status_code=404, detail="Feature not available for faculty/support users")
        if not isinstance(type, str) or type.lower() not in ['system', 'course']:
            raise ValueError("Notification type is invalid")
        
        try:
            result = await db.execute(select(CourseNotification)
                                .where(
                                    and_(CourseNotification.id == notification_id,
                                          CourseNotification.type == type)
                                    )
                                )
            notif = result.scalars().first()
            if(notif):
                logger.info(f"Course Notification found going to check and update in status table")
                notif_status_result = await db.execute(select(UserNotificationStatus)
                                      .where(
                                        and_(UserNotificationStatus.notification_id == notification_id,
                                            UserNotificationStatus.type == type,
                                            UserNotificationStatus.user_id == user_id)
                                        )
                                    )
                notif_status = notif_status_result.scalars().first()
                if(notif_status):
                    logger.info(f"Marking as read")
                    notif_status.read = True
                    db.add(notif_status)
                    await db.commit()
                    logger.info(f"Notification updated as read")
                    return notif_status
                else:
                    logger.info(f"Sys notif record not found in status table")
                    await db.rollback()
            else:
                logger.info(f"Course Notification not found going to check for sys")
                sys_notif_result = await db.execute(select(SystemNotification)
                                      .where(
                                        and_(SystemNotification.id == notification_id,
                                            SystemNotification.type == type)
                                        )
                                    )
                sys_notif = sys_notif_result.scalars().first()
                if(sys_notif):
                    logger.info(f"Sys Notification found going to check and update in status table")
                    sys_notif_status_result = await db.execute(select(UserNotificationStatus)
                                      .where(
                                        and_(UserNotificationStatus.notification_id == notification_id,
                                            UserNotificationStatus.type == type,
                                            UserNotificationStatus.user_id == user_id)
                                        )
                                    )
                    sys_notif_status = sys_notif_status_result.scalars().first()
                    if(sys_notif_status):
                        logger.info(f"Going to update sys notif as read")
                        sys_notif_status.read = True
                        db.add(sys_notif_status)
                        await db.commit()
                        logger.info(f"Sys Notification updated as read")
                        return sys_notif_status
                    else:
                        logger.info(f"Sys notif record not found in status table")
                        await db.rollback()
            await db.rollback() 
            raise HTTPException(status_code=404, detail="Notification not found")
        except Exception as e:
            await db.rollback() 
            logger.error(f"Error saving notification: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @staticmethod
    async def markAllNotificationAsRead(notifications: List[Dict[str, str]], db: AsyncSession, user_id: str):
        logger.info("Inside markAllNotificationAsRead in NotificationService")
        
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() in ['faculty', 'support']:
            logger.info(f"For faculty this feature is not available")
            raise HTTPException(status_code=404, detail="Feature not available for faculty/support users")

        if not isinstance(type, str) or type.lower() not in ['system', 'course']:
            raise ValueError("Notification type is invalid")
        try:
            updated_notifications = []
            for notif in notifications:
                notification_id = notif.get("id")
                notification_type = notif.get("type")

                result = await db.execute(
                    select(UserNotificationStatus).where(
                        and_(UserNotificationStatus.notification_id == notification_id),
                        (UserNotificationStatus.user_id == user_id), (UserNotificationStatus.type==notification_type)
                    )
                )
                notif_status = result.scalars().first()
                logger.info(f"Notification found Going to mark as read {notification_id}")
                if notif_status:
                    notif_status.read = True
                    db.add(notif_status)
                    updated_notifications.append(notif_status)
                else:
                    raise HTTPException(status_code=404, detail=f"Notification with id = {notification_id} not found")

            await db.commit()
            return updated_notifications
        
        except Exception as e:
            await db.rollback()
            logger.error(f"Error marking notifications as read: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def delete_notification_by_id(notification_id: int, type:str, db: AsyncSession,user_id:UUID):
        logger.info(f"In delete_notification_by_id in NotificationService class with id = {notification_id}, type={type}")
        
        if not isinstance(type, str) or type.lower() not in ['system', 'course']:
            raise ValueError("Notification type is invalid")
        
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['support', 'faculty']:
            logger.info(f"You do not have permission to delete this notification")
            raise HTTPException(status_code=403, detail="You are forbidden to user the resource")
        
        course_notification_found = True

        try:
            result = await db.execute(select(CourseNotification)
                                .where(
                                    and_(CourseNotification.id == notification_id,
                                          CourseNotification.type == type)
                                    )
                                )
            notif = result.scalars().first()
            if not notif:
                logger.info("CourseNotification not found. Will check for sys notification")
                course_notification_found = False
            
            if not course_notification_found:
                sys_notif_result = await db.execute(select(SystemNotification)
                                    .where(
                                        and_(SystemNotification.id == notification_id,
                                            SystemNotification.type == type)
                                        )
                                    )
                sys_notif = sys_notif_result.scalars().first()

                if not sys_notif:
                    raise HTTPException(status_code=404, detail="No Nodification found")
            
            logger.info("Notification found, checking UserNotificationStatus before deletion.")
            notif_status_result = await db.execute(select(UserNotificationStatus)
                                      .where(
                                        and_(UserNotificationStatus.notification_id == notification_id,
                                            UserNotificationStatus.type == type,
                                            UserNotificationStatus.user_id == user_id)
                                        )
                                    )
            notif_status = notif_status_result.scalars().first()
            # Delete both records
            if notif_status:
                await db.delete(notif_status)
                logger.info("Deleted UserNotificationStatus record.")
            
            if not course_notification_found and sys_notif:
                await db.delete(sys_notif)
                logger.info("Deleted Sys notifiction record.")

            if course_notification_found and notif:
                await db.delete(notif)
                logger.info("Deleted CourseNotification record.")

            # Commit the transaction
            await db.commit()
            return 
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting the notification : {str(e)}")
            raise HTTPException(status_code=500, detail="Notification deletion failed")
               


