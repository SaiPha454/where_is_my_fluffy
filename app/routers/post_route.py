from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List

from ..db.database import get_db
from ..services.post_service import PostService
from ..services.report_service import ReportService
from ..repositories.post_repository import PostRepository
from ..repositories.report_repository import ReportRepository
from ..repositories.user_repository import UserRepository
from ..schemas.post_schema import PostCreateForm, PostResponse, PostListResponse, PostFilters, PostStatus
from ..schemas.report_schema import ReportResponse
from ..routers.auth_route import get_current_user
from ..schemas.auth_schema import UserResponse

router = APIRouter(prefix="/posts", tags=["posts"])


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    """Dependency to get PostService instance"""
    post_repository = PostRepository(db)
    user_repository = UserRepository(db)
    return PostService(post_repository, user_repository)


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """Dependency to get ReportService instance"""
    report_repository = ReportRepository(db)
    post_repository = PostRepository(db)
    user_repository = UserRepository(db)
    return ReportService(report_repository, post_repository, user_repository, db)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_form: PostCreateForm = Depends(PostCreateForm.as_form),
    photos: List[UploadFile] = File(..., description="Pet photos (1-4 images, max 5MB each)"),
    current_user: UserResponse = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """
    Create a new post for a lost pet.
    
    Requires authentication. The authenticated user will be set as the owner of the post.
    
    Form Data:
    - pet_name: Name of the pet
    - pet_species: Species (Dog, Cat, etc.)
    - pet_breed: Breed (optional)
    - last_seen_location: Last known location
    - contact_information: Contact details
    - description: Additional description (optional)
    - reward_points: Reward points offered (default: 0)
    - photos: 1-4 image files (JPG, PNG, GIF, WebP)
    
    Image Requirements:
    - 1-4 photos required
    - Max 5MB per image
    - Supported formats: JPG, JPEG, PNG, GIF, WebP
    - Images will be automatically resized if too large
    """
    return await post_service.create_post(post_form, photos, current_user.id)


@router.get("/", response_model=PostListResponse)
async def get_posts(
    status: Optional[PostStatus] = Query(None, description="Filter by post status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    post_service: PostService = Depends(get_post_service)
):
    """
    Get all posts with optional filtering.
    
    Query Parameters:
    - status: Filter by post status (lost, found, closed)
    - user_id: Filter by user ID to get posts from a specific user
    
    Examples:
    - GET /posts - Get all posts
    - GET /posts?status=lost - Get only lost pet posts
    - GET /posts?status=found - Get only found pet posts
    - GET /posts?status=closed - Get only closed posts
    - GET /posts?user_id=123 - Get all posts by user 123
    - GET /posts?status=lost&user_id=123 - Get lost pet posts by user 123
    """
    filters = PostFilters(status=status, user_id=user_id)
    return post_service.get_posts(filters)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(
    post_id: int,
    post_service: PostService = Depends(get_post_service)
):
    """
    Get detailed information about a specific post by ID.
    
    Returns the post with all related information:
    - Post details
    - Owner information
    - Photos
    - Reward information (if any)
    """
    return post_service.get_post_by_id(post_id)


@router.put("/{post_id}", response_model=PostResponse)
async def mark_post_as_found(
    post_id: int,
    current_user: UserResponse = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """
    Mark a post as found (change status from lost to found).
    
    Only the owner of the post can update its status.
    Requires authentication.
    """
    return post_service.mark_post_as_found(post_id, current_user.id)


@router.delete("/{post_id}", response_model=PostResponse)
async def close_post(
    post_id: int,
    current_user: UserResponse = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """
    Close a post (change status to closed).
    
    This marks the post as no longer active. Once closed, the post 
    won't appear in normal searches.
    
    Only the owner of the post can close it.
    Requires authentication.
    """
    return post_service.close_post(post_id, current_user.id)


@router.get("/{post_id}/reports", response_model=List[ReportResponse])
async def get_post_reports(
    post_id: int,
    report_service: ReportService = Depends(get_report_service)
):
    """
    Get all reports for a specific post.
    
    Returns a list of all reports related to the given post ID,
    sorted by creation date with the latest report first.
    Each report includes the reported user information.
    
    Path Parameters:
    - post_id: The ID of the post to get reports for
    
    Returns:
    - List of reports with reporter information, sorted by creation date (latest first)
    """
    return report_service.get_reports_by_post_id(post_id)
