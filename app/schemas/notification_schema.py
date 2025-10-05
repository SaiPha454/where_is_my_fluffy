from pydantic import BaseModel
from typing import List
from datetime import datetime
from enum import Enum


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"


class NotificationResponse(BaseModel):
    """Response schema for notification"""
    id: int
    post_id: int
    report_id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Response schema for list of notifications"""
    notifications: List[NotificationResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "notifications": [
                    {
                        "id": 1,
                        "post_id": 1,
                        "report_id": 1,
                        "message": "New report on your post",
                        "is_read": False,
                        "created_at": "2025-10-03T10:30:00"
                    }
                ],
                "total": 1
            }
        }


class NotificationUpdateResponse(BaseModel):
    """Response schema for notification update operations"""
    message: str
    updated_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Notifications marked as read successfully",
                "updated_count": 3
            }
        }