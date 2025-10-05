from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, update
from ..models.notification import Notification
from typing import List, Optional


class NotificationRepository:
    """Repository layer for notification operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_unread_notifications_by_post_id(self, post_id: int) -> List[Notification]:
        """Get all unread notifications for a specific post"""
        return (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.post_id == post_id,
                    Notification.is_read == False
                )
            )
            .order_by(Notification.created_at.desc())
            .all()
        )
    
    def mark_notifications_as_read_by_post_id(self, post_id: int) -> int:
        """Mark all notifications for a specific post as read and return count of updated records"""
        try:
            # Update all unread notifications for the post
            result = self.db.execute(
                update(Notification)
                .where(
                    and_(
                        Notification.post_id == post_id,
                        Notification.is_read == False
                    )
                )
                .values(is_read=True)
            )
            
            self.db.commit()
            return result.rowcount  # Number of rows affected
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def create_notification(self, post_id: int, report_id: int, message: str) -> Optional[Notification]:
        """Create a new notification"""
        try:
            notification = Notification(
                post_id=post_id,
                report_id=report_id,
                message=message,
                is_read=False
            )
            self.db.add(notification)
            self.db.commit()
            return notification
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get a notification by ID"""
        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )
    
    def post_exists(self, post_id: int) -> bool:
        """Check if a post exists (used for validation)"""
        from ..models.post import Post
        return self.db.query(Post).filter(Post.id == post_id).first() is not None
