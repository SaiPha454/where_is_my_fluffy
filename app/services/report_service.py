from ..repositories.report_repository import ReportRepository
from ..repositories.post_repository import PostRepository
from ..schemas.report_schema import ReportCreateForm, ReportResponse
from ..builders.report_builder import ReportBuilder
from ..models.report import ReportStatus
from ..models.post import PostStatus
from ..utils.file_upload import file_upload_manager
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List


class ReportService:
    """Service layer for report operations"""
    
    def __init__(self, report_repository: ReportRepository, post_repository: PostRepository):
        self.report_repository = report_repository
        self.post_repository = post_repository
    
    async def create_report(
        self, 
        report_form: ReportCreateForm, 
        photos: Optional[List[UploadFile]], 
        reporter_id: int
    ) -> ReportResponse:
        """Create a new report with optional file uploads using Builder pattern"""
        try:
            # Step 1: Validate that the post exists and is still active
            post = self.post_repository.get_post_by_id(report_form.post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {report_form.post_id} not found"
                )
            
            # Check if post is closed or found - no reports allowed
            if post.status in [PostStatus.closed, PostStatus.found]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot submit report for a post that is already {post.status.value}"
                )
            
            # Step 2: Handle file uploads (if any)
            photo_paths = []
            if photos:
                if len(photos) > 4:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Maximum 4 photos allowed per report"
                    )
                photo_paths = await file_upload_manager.save_multiple_files(photos)
            
            try:
                # Step 3: Create ReportBuilder with individual methods
                builder = (ReportBuilder()
                    .set_post_id(report_form.post_id)
                    .set_reporter_id(reporter_id)
                    .set_description(report_form.description)
                    .set_location(report_form.location)
                    .set_photos(photo_paths)
                    .set_status(ReportStatus.pending))  # Always pending for new reports
                
                # Step 4: Repository uses builder's getter methods and triggers observer
                new_report = self.report_repository.create_report(builder)
                
                if not new_report:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create report"
                    )
                
                return ReportResponse.from_report(new_report)
                
            except ValueError as e:
                # Builder validation error - cleanup files and return user-friendly error
                for photo_path in photo_paths:
                    file_upload_manager.delete_file(photo_path)
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid report data: {str(e)}"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            # Cleanup uploaded files on any error
            if 'photo_paths' in locals():
                for photo_path in photo_paths:
                    file_upload_manager.delete_file(photo_path)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating report: {str(e)}"
            )
    
    def get_report_by_id(self, report_id: int) -> ReportResponse:
        """Get a specific report by ID with all related data"""
        try:
            report = self.report_repository.get_report_by_id(report_id)
            
            if not report:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Report with id {report_id} not found"
                )
            
            return ReportResponse.from_report(report)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving report: {str(e)}"
            )
    
    def reject_report(self, report_id: int) -> ReportResponse:
        """Reject a report (set status to rejected)"""
        try:
            # Check if report exists
            if not self.report_repository.report_exists(report_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Report with id {report_id} not found"
                )
            
            # Update the report status
            updated_report = self.report_repository.reject_report(report_id)
            
            if not updated_report:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to reject report"
                )
            
            return ReportResponse.from_report(updated_report)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error rejecting report: {str(e)}"
            )
    
    def reward_report(self, report_id: int) -> ReportResponse:
        """Reward a report (set status to rewarded)"""
        try:
            # Check if report exists
            if not self.report_repository.report_exists(report_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Report with id {report_id} not found"
                )
            
            # Update the report status
            updated_report = self.report_repository.reward_report(report_id)
            
            if not updated_report:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to reward report"
                )
            
            return ReportResponse.from_report(updated_report)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error rewarding report: {str(e)}"
            )