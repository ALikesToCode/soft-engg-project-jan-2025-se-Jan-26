from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import CourseNotification, SystemNotification ,UserNotificationStatus
from app.models.course import CourseEnrollment
from app.models.user import User
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy import select
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class NotificationService:

    @staticmethod
    async def get_user_notification(db: AsyncSession, user_id: UUID):
        logger.info("Just entered in get_user_notification in NotificationService class")
        try:
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
    async def save_course_notification(notification_content,db: AsyncSession,user_id:UUID):
        logger.info("Just entered in save_course_notification in NotificationService class")
    
        try:
            notification = CourseNotification(
                type=notification_content.type,
                priority=notification_content.priority,
                category=notification_content.category,
                title=notification_content.title,
                message=notification_content.message,
                timestamp=datetime.utcnow(),
                course_id=notification_content.courseId
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
        try:
            sys_notification = SystemNotification(
                type=sys_notification_content.type,
                priority=sys_notification_content.priority,
                category=sys_notification_content.category,
                title=sys_notification_content.title,
                message=sys_notification_content.message,
                timestamp=datetime.utcnow(),
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



