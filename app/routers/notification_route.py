from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..services.notification_service import NotificationService
from ..repositories.notification_repository import NotificationRepository
from ..schemas.notification_schema import NotificationUpdateResponse
from ..routers.auth_route import get_current_user
from ..schemas.auth_schema import UserResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """Dependency to get NotificationService instance"""
    notification_repository = NotificationRepository(db)
    return NotificationService(notification_repository)


@router.patch("/", response_model=NotificationUpdateResponse)
async def mark_notifications_as_read(
    post_id: int = Query(..., description="ID of the post to mark notifications as read"),
    current_user: UserResponse = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Mark all notifications for a specific post as read.
    
    This endpoint will update all unread notification records related to the specified post_id
    to have their status marked as read.
    
    Query Parameters:
    - post_id: The ID of the post for which to mark notifications as read (required)
    
    Returns:
    - message: Success message
    - updated_count: Number of notifications that were updated
    
    Requires authentication.
    """
    return notification_service.mark_notifications_as_read(post_id)
