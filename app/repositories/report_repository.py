from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from ..models.report import Report, ReportStatus
from ..models.report_photo import ReportPhoto
from ..observers.report_observer import report_event_manager, NotificationObserver
from typing import Optional, List
from datetime import datetime


class ReportRepository:
    """Repository layer for report operations"""
    
    def __init__(self, db: Session):
        self.db = db
        # Set up notification observer only once
        self._setup_observers()
    
    def _setup_observers(self):
        """Set up observers for report events (only if not already set up)"""
        # Check if notification observer is already registered
        notification_observer_exists = any(
            isinstance(observer, NotificationObserver) 
            for observer in report_event_manager._observers
        )
        
        if not notification_observer_exists:
            notification_observer = NotificationObserver(self.db)
            report_event_manager.add_observer(notification_observer)
    
    def create_report(self, builder) -> Optional[Report]:
        """
        Create a new report from builder using getter methods
        
        Uses builder's getter methods for clean access and triggers
        notification observer when report is successfully created.
        """
        try:
            # Create the main report entity using builder getter methods
            new_report = Report(
                post_id=builder.get_post_id(),
                reporter_id=builder.get_reporter_id(),
                description=builder.get_description(),
                location=builder.get_location(),
                status=builder.get_status()  # Always pending for new reports
            )
            self.db.add(new_report)
            self.db.flush()  # Get the report ID for related entities
            
            # Create report photos using builder getter methods
            for photo_url in builder.get_photos():
                report_photo = ReportPhoto(
                    report_id=new_report.id,
                    photo_url=photo_url
                )
                self.db.add(report_photo)
            
            self.db.commit()
            
            # Get the complete report with relationships for the observer
            created_report = self.get_report_by_id(new_report.id)
            
            # Trigger notification observer
            if created_report:
                report_event_manager.notify_report_created(created_report)
            
            return created_report
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_report_by_id(self, report_id: int) -> Optional[Report]:
        """Get a report by ID with all related data"""
        return (
            self.db.query(Report)
            .options(
                joinedload(Report.reporter),  # User information
                joinedload(Report.post),      # Post information
                joinedload(Report.photos)     # Report photos
            )
            .filter(Report.id == report_id)
            .first()
        )
    
    def update_report_status(self, report_id: int, status: ReportStatus) -> Optional[Report]:
        """Update report status"""
        try:
            report = self.db.query(Report).filter(Report.id == report_id).first()
            if not report:
                return None
            
            report.status = status
            self.db.commit()
            
            # Return updated report with relationships
            return self.get_report_by_id(report.id)
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def reject_report(self, report_id: int) -> Optional[Report]:
        """Reject a report (set status to rejected)"""
        return self.update_report_status(report_id, ReportStatus.rejected)
    
    def reward_report(self, report_id: int) -> Optional[Report]:
        """Reward a report (set status to rewarded)"""
        return self.update_report_status(report_id, ReportStatus.rewarded)
    
    def report_exists(self, report_id: int) -> bool:
        """Check if a report exists"""
        return self.db.query(Report).filter(Report.id == report_id).first() is not None
    
    def get_reports_by_post_id(self, post_id: int) -> List[Report]:
        """Get all reports for a specific post, sorted by creation date (latest first)"""
        return (
            self.db.query(Report)
            .options(
                joinedload(Report.reporter),  # Include reported user information
                joinedload(Report.post),      # Include post information
                joinedload(Report.photos)     # Include report photos
            )
            .filter(Report.post_id == post_id)
            .order_by(Report.created_at.desc())  # Latest first
            .all()
        )
    
    def update_reports_by_post_and_status(self, post_id: int, current_status: ReportStatus, new_status: ReportStatus) -> List[Report]:
        """Update all reports for a specific post that have a certain status to a new status"""
        try:
            # Get all reports matching the criteria
            reports_to_update = (
                self.db.query(Report)
                .filter(
                    Report.post_id == post_id,
                    Report.status == current_status
                )
                .all()
            )
            
            # Update their status
            updated_reports = []
            for report in reports_to_update:
                report.status = new_status
                updated_reports.append(report)
            
            if updated_reports:
                self.db.commit()
                
                # Return updated reports with full relationships
                updated_report_ids = [report.id for report in updated_reports]
                return (
                    self.db.query(Report)
                    .options(
                        joinedload(Report.reporter),
                        joinedload(Report.post),
                        joinedload(Report.photos)
                    )
                    .filter(Report.id.in_(updated_report_ids))
                    .all()
                )
            
            return []
            
        except Exception as e:
            self.db.rollback()
            raise e