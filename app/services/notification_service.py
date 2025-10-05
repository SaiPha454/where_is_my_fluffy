from ..repositories.notification_repository import NotificationRepository
from ..schemas.notification_schema import NotificationResponse, NotificationUpdateResponse
from fastapi import HTTPException, status
from typing import List


class NotificationService:
    """Service layer for notification operations"""
    
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository
    
    def get_unread_notifications_by_post_id(self, post_id: int) -> List[NotificationResponse]:
        """Get all unread notifications for a specific post"""
        try:
            notifications = self.notification_repository.get_unread_notifications_by_post_id(post_id)
            return [NotificationResponse.model_validate(notification) for notification in notifications]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving notifications: {str(e)}"
            )
    
    def mark_notifications_as_read(self, post_id: int) -> NotificationUpdateResponse:
        """Mark all notifications for a post as read"""
        try:
            # Validate that the post exists
            if not self.notification_repository.post_exists(post_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {post_id} not found"
                )
            
            # Mark notifications as read
            updated_count = self.notification_repository.mark_notifications_as_read_by_post_id(post_id)
            
            return NotificationUpdateResponse(
                message="Notifications marked as read successfully",
                updated_count=updated_count
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating notifications: {str(e)}"
            )
    
    def create_notification(self, post_id: int, report_id: int, message: str) -> NotificationResponse:
        """Create a new notification"""
        try:
            notification = self.notification_repository.create_notification(post_id, report_id, message)
            if not notification:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create notification"
                )
            
            return NotificationResponse.model_validate(notification)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating notification: {str(e)}"
            )
