from ..repositories.post_repository import PostRepository
from ..repositories.user_repository import UserRepository
from ..schemas.post_schema import PostCreateForm, PostResponse, PostListResponse, PostFilters
from ..models.post import Post, PostStatus
from ..utils.file_upload import file_upload_manager
from ..builders.post_builder import PostBuilder
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List


class PostService:
    """Service layer for post operations"""
    
    def __init__(self, post_repository: PostRepository, user_repository: UserRepository):
        self.post_repository = post_repository
        self.user_repository = user_repository
    
    async def create_post(self, post_form: PostCreateForm, photos: List[UploadFile], owner_id: int) -> PostResponse:
        """Create a new post with file uploads using Builder pattern"""
        try:
            # Step 1: Handle file uploads (this stays the same)
            photo_paths = await file_upload_manager.save_multiple_files(photos)
            
            try:
                # Step 2: Validate user balance for reward points
                reward_amount = post_form.reward_points or 0
                user = None  # Store user data to avoid duplicate queries
                if reward_amount > 0:
                    user = self.user_repository.get_user_by_id(owner_id)
                    if not user:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found"
                        )
                    
                    if user.balance < reward_amount:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Insufficient balance. You have {user.balance} points but need {reward_amount} points for this reward."
                        )
                
                # Step 3: Create PostBuilder with individual methods (as requested)
                builder = (PostBuilder()
                    .set_owner_id(owner_id)
                    .set_pet_name(post_form.pet_name)
                    .set_pet_species(post_form.pet_species)
                    .set_pet_breed(post_form.pet_breed)
                    .set_last_seen_location(post_form.last_seen_location)
                    .set_contact_information(post_form.contact_information)
                    .set_description(post_form.description)
                    .set_photos(photo_paths)
                    .set_reward_points(reward_amount)  # Use validated reward amount
                    .set_status(PostStatus.lost))  # Use proper enum
                
                # Step 4: Repository uses builder's getter methods for clean access
                new_post = self.post_repository.create_post(builder)
                
                if not new_post:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create post"
                    )
                
                # Step 5: Deduct reward points from user's balance if any
                if reward_amount > 0 and user:  # user is already retrieved above
                    new_balance = user.balance - reward_amount
                    updated_user = self.user_repository.update_user_balance(owner_id, new_balance)
                    if not updated_user:
                        # This is a serious error - post created but balance not updated
                        # In a real system, you might want to implement compensation logic
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Post created but failed to update balance. Please contact support."
                        )
                
                return PostResponse.from_post(new_post)
                
            except ValueError as e:
                # Builder validation error - cleanup files and return user-friendly error
                for photo_path in photo_paths:
                    file_upload_manager.delete_file(photo_path)
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid post data: {str(e)}"
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
