from abc import ABC, abstractmethod
from typing import Any, List
from ..models.report import Report


class ReportObserver(ABC):
    """Abstract observer for report events"""
    
    @abstractmethod
    def on_report_created(self, report: Report) -> None:
        """Called when a new report is created"""
        pass


class NotificationObserver(ReportObserver):
    """Observer that creates notifications when reports are created"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    def on_report_created(self, report: Report) -> None:
        """Create a notification when a new report is submitted"""
        from ..models.notification import Notification
        
        try:
            # Create notification for the post owner
            notification = Notification(
                post_id=report.post_id,
                report_id=report.id,
                message="New report submission",  # Hardcoded as requested
                is_read=False  # Default for new notifications
            )
            
            self.db_session.add(notification)
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            # Log error but don't fail the report creation
            print(f"Error creating notification: {e}")


class ReportEventManager:
    """Manages report observers and triggers events"""
    
    def __init__(self):
        self._observers: List[ReportObserver] = []
    
    def add_observer(self, observer: ReportObserver) -> None:
        """Add an observer to receive report events"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: ReportObserver) -> None:
        """Remove an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_report_created(self, report: Report) -> None:
        """Notify all observers that a report was created"""
        for observer in self._observers:
            try:
                observer.on_report_created(report)
            except Exception as e:
                # Log error but continue with other observers
                print(f"Observer {observer.__class__.__name__} failed: {e}")


# Global event manager instance
report_event_manager = ReportEventManager()