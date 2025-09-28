from ..repositories.post_repository import PostRepository
from ..schemas.post_schema import PostCreate, PostCreateForm, PostResponse, PostListResponse, PostFilters
from ..models.post import Post
from ..utils.file_upload import file_upload_manager
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List


class PostService:
    """Service layer for post operations"""
    
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    async def create_post(self, post_form: PostCreateForm, photos: List[UploadFile], owner_id: int) -> PostResponse:
        """Create a new post with file uploads"""
        try:
            # Validate and save uploaded photos
            photo_paths = await file_upload_manager.save_multiple_files(photos)
            
            # Create PostCreate object with photo paths
            post_data = PostCreate(
                pet_name=post_form.pet_name,
                pet_species=post_form.pet_species,
                pet_breed=post_form.pet_breed,
                last_seen_location=post_form.last_seen_location,
                contact_information=post_form.contact_information,
                description=post_form.description,
                photos=photo_paths,
                reward_points=post_form.reward_points
            )
            
            # Create the post through repository
            new_post = self.post_repository.create_post(post_data, owner_id)
            
            if not new_post:
                # Cleanup uploaded files if post creation failed
                for photo_path in photo_paths:
                    file_upload_manager.delete_file(photo_path)
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create post"
                )
            
            return PostResponse.from_post(new_post)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating post: {str(e)}"
            )
    
    def get_posts(self, filters: PostFilters) -> PostListResponse:
        """Get posts with optional filtering"""
        try:
            # Get posts from repository
            posts = self.post_repository.get_posts(
                status=filters.status,
                user_id=filters.user_id
            )
            
            # Get total count
            total_count = self.post_repository.get_posts_count(
                status=filters.status,
                user_id=filters.user_id
            )
            
            # Convert to response format
            post_responses = [PostResponse.from_post(post) for post in posts]
            
            return PostListResponse(
                posts=post_responses,
                total=total_count
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving posts: {str(e)}"
            )
    
    def get_post_by_id(self, post_id: int) -> PostResponse:
        """Get a specific post by ID"""
        try:
            post = self.post_repository.get_post_by_id(post_id)
            
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {post_id} not found"
                )
            
            return PostResponse.from_post(post)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving post: {str(e)}"
            )
    
    def mark_post_as_found(self, post_id: int, current_user_id: Optional[int] = None) -> PostResponse:
        """Mark a post as found (only owner can do this for their own posts)"""
        try:
            # Check if post exists
            if not self.post_repository.post_exists(post_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {post_id} not found"
                )
            
            # If user_id is provided, check ownership
            if current_user_id is not None:
                if not self.post_repository.is_post_owner(post_id, current_user_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only update your own posts"
                    )
            
            # Update the post status
            updated_post = self.post_repository.mark_post_as_found(post_id, current_user_id)
            
            if not updated_post:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update post status"
                )
            
            return PostResponse.from_post(updated_post)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating post: {str(e)}"
            )
    
    def close_post(self, post_id: int, current_user_id: Optional[int] = None) -> PostResponse:
        """Close a post (only owner can do this for their own posts)"""
        try:
            # Check if post exists
            if not self.post_repository.post_exists(post_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {post_id} not found"
                )
            
            # If user_id is provided, check ownership
            if current_user_id is not None:
                if not self.post_repository.is_post_owner(post_id, current_user_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only close your own posts"
                    )
            
            # Close the post
            closed_post = self.post_repository.close_post(post_id, current_user_id)
            
            if not closed_post:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to close post"
                )
            
            return PostResponse.from_post(closed_post)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error closing post: {str(e)}"
            )
    
    def validate_post_ownership(self, post_id: int, user_id: int) -> bool:
        """Validate that a user owns a specific post"""
        return self.post_repository.is_post_owner(post_id, user_id)
