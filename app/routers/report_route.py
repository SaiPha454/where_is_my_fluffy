from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List

from ..db.database import get_db
from ..services.report_service import ReportService
from ..repositories.report_repository import ReportRepository
from ..repositories.post_repository import PostRepository
from ..repositories.user_repository import UserRepository
from ..schemas.report_schema import ReportCreateForm, ReportResponse
from ..schemas.auth_schema import UserResponse
from ..routers.auth_route import get_current_user

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)]
)


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """Dependency to get ReportService instance"""
    report_repository = ReportRepository(db)
    post_repository = PostRepository(db)
    user_repository = UserRepository(db)
    return ReportService(report_repository, post_repository, user_repository, db)


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED, responses={
    401: {"content": {"application/json": {"examples": {"MissingSession": {"summary": "Missing session cookie", "value": {"detail": "Authentication required"}}, "InvalidSession": {"summary": "Invalid or expired session", "value": {"detail": "Invalid or expired session"}}}}}},
    404: {"description": "Post not found", "content": {"application/json": {"example": {"detail": "Post with id 123 not found"}}}},
    400: {"content": {"application/json": {"examples": {"PostNotActive": {"summary": "Post not active", "value": {"detail": "Cannot submit report for a post that is already <status>"}}, "TooManyPhotos": {"summary": "Too many photos", "value": {"detail": "Maximum 4 photos allowed per report"}}, "InvalidReportData": {"summary": "Builder validation failed", "value": {"detail": "Invalid report data: <reason>"}}, "FailedCreateReport": {"summary": "Failed to create report", "value": {"detail": "Failed to create report"}}}}}},
    500: {"description": "Server error while creating report", "content": {"application/json": {"example": {"detail": "Error creating report: <reason>"}}}}
})
async def create_report(
    post_id: int = Form(...),
    description: str = Form(...),
    location: Optional[str] = Form(None),
    photos: Optional[List[UploadFile]] = File(None),
    current_user: UserResponse = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Create a new report for a specific post
    
    - **post_id**: ID of the post being reported about
    - **description**: Description of the report (required)
    - **location**: Location where the pet was found (optional)
    - **photos**: Optional photos (max 4)
    """
    # Create form data from the inputs
    report_form = ReportCreateForm(
        post_id=post_id,
        description=description,
        location=location
    )
    
    # Use authenticated user's ID as reporter_id
    return await report_service.create_report(
        report_form=report_form,
        photos=photos,
        reporter_id=current_user.id
    )


@router.get("/{report_id}", response_model=ReportResponse, responses={
    401: {"content": {"application/json": {"examples": {"MissingSession": {"summary": "Missing session cookie", "value": {"detail": "Authentication required"}}, "InvalidSession": {"summary": "Invalid or expired session", "value": {"detail": "Invalid or expired session"}}}}}},
    404: {"description": "Report not found", "content": {"application/json": {"example": {"detail": "Report with id 123 not found"}}}},
    500: {"description": "Server error while retrieving report", "content": {"application/json": {"example": {"detail": "Error retrieving report: <reason>"}}}}
})
def get_report(
    report_id: int,
    current_user: UserResponse = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Get details of a specific report by ID
    
    Returns report details including:
    - Reporter information
    - Related post information
    - Report photos
    - Report status and timestamps
    """
    return report_service.get_report_by_id(report_id)


@router.put("/{report_id}/reject", response_model=ReportResponse, responses={
    401: {"content": {"application/json": {"examples": {"MissingSession": {"summary": "Missing session cookie", "value": {"detail": "Authentication required"}}, "InvalidSession": {"summary": "Invalid or expired session", "value": {"detail": "Invalid or expired session"}}}}}},
    404: {"description": "Report not found", "content": {"application/json": {"example": {"detail": "Report with id 123 not found"}}}},
    400: {"description": "Failed to reject report", "content": {"application/json": {"example": {"detail": "Failed to reject report"}}}},
    500: {"description": "Server error while rejecting report", "content": {"application/json": {"example": {"detail": "Error rejecting report: <reason>"}}}}
})
def reject_report(
    report_id: int,
    current_user: UserResponse = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Reject a report by changing its status to 'rejected'
    
    This endpoint allows authorized users to reject a report,
    typically used by post owners or administrators.
    """
    return report_service.reject_report(report_id)


@router.put("/{report_id}/reward", response_model=ReportResponse, responses={
    401: {"content": {"application/json": {"examples": {"MissingSession": {"summary": "Missing session cookie", "value": {"detail": "Authentication required"}}, "InvalidSession": {"summary": "Invalid or expired session", "value": {"detail": "Invalid or expired session"}}}}}},
    404: {"description": "Report not found", "content": {"application/json": {"example": {"detail": "Report with id 123 not found"}}}},
    400: {"description": "Failed to reward report", "content": {"application/json": {"example": {"detail": "Failed to reward report"}}}},
    500: {"description": "Server error during reward processing", "content": {"application/json": {"examples": {"RelatedPostMissing": {"summary": "Related post not found", "value": {"detail": "Related post not found"}}, "ReporterMissing": {"summary": "Reporter not found", "value": {"detail": "Reporter not found"}}, "FailedUpdateBalance": {"summary": "Failed to update reporter balance", "value": {"detail": "Failed to update reporter balance"}}, "MarkPostFoundFailed": {"summary": "Failed to mark post as found", "value": {"detail": "Failed to mark post as found"}}, "UnexpectedServerError": {"summary": "Unexpected server error", "value": {"detail": "Error processing reward: <reason>"}}}}}}
})
def reward_report(
    report_id: int,
    current_user: UserResponse = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Reward a report by changing its status to 'rewarded'
    
    This endpoint allows authorized users to mark a report as rewarded,
    typically used when the report leads to finding the lost pet.
    """
    return report_service.reward_report(report_id)