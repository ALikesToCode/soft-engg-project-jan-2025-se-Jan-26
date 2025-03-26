from datetime import datetime
from pydantic import BaseModel, ValidationError, constr, validator
from uuid import UUID
from typing import ClassVar

class CourseNotificationSchema(BaseModel):
    PRIORITY_LEVELS: ClassVar[set[str]] = {"low", "high", "urgent", "medium"}
    CATEGORY_OPTIONS: ClassVar[set[str]] = {"announcement", "assignment", "grade"}

    type: str
    priority: constr(strip_whitespace=True, min_length=1)  # type: ignore
    category: constr(strip_whitespace=True, min_length=1)  # type: ignore
    title: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    message: constr(strip_whitespace=True, min_length=1)  # type: ignore
    courseId: UUID  # Ensures it's a valid UUID

    @validator("type")
    def validate_type(cls, value):
        if value.lower() != "course":
            raise ValueError("Invalid type: Must be 'course'")
        return value

    @validator("priority")
    def validate_priority(cls, value):
        if value.lower() not in cls.PRIORITY_LEVELS:
            raise ValueError(f"Invalid priority: Must be one of {cls.PRIORITY_LEVELS}")
        return value.lower()

    @validator("category")
    def validate_category(cls, value):
        if value.lower() not in cls.CATEGORY_OPTIONS:
            raise ValueError(f"Invalid category: Must be one of {cls.CATEGORY_OPTIONS}")
        return value.lower()


class SystemNotificationSchema(BaseModel):
    PRIORITY_LEVELS: ClassVar[set[str]] = {"low", "high", "urgent", "medium"}
    CATEGORY_OPTIONS: ClassVar[set[str]] = {"announcement", "assignment", "grade", "maintenance", "technical"}

    type: str
    priority: constr(strip_whitespace=True, min_length=1)  # type: ignore
    category: constr(strip_whitespace=True, min_length=1)  # type: ignore
    title: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    message: constr(strip_whitespace=True, min_length=1)  # type: ignore

    @validator("type")
    def validate_type(cls, value):
        if value.lower() != "system":
            raise ValueError("Invalid type: Must be 'system'")
        return value

    @validator("priority")
    def validate_priority(cls, value):
        if value.lower() not in cls.PRIORITY_LEVELS:
            raise ValueError(f"Invalid priority: Must be one of {cls.PRIORITY_LEVELS}")
        return value.lower()

    @validator("category")
    def validate_category(cls, value):
        if value.lower() not in cls.CATEGORY_OPTIONS:
            raise ValueError(f"Invalid category: Must be one of {cls.CATEGORY_OPTIONS}")
        return value.lower()


class NotificationValidator:
    @staticmethod
    def validate_course_notification(course_notification_data: dict):
        try:
            validated_data = CourseNotificationSchema(**course_notification_data)
            return validated_data.dict()  # Return validated dictionary
        except ValidationError as e:
            raise ValueError(f"Invalid course notification data: {e.errors()}")

    @staticmethod
    def validate_system_notification(system_notification_data: dict):
        try:
            validated_data = SystemNotificationSchema(**system_notification_data)
            return validated_data.dict()  # Return validated dictionary
        except ValidationError as e:
            raise ValueError(f"Invalid system notification data: {e.errors()}")
