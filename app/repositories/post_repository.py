from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from ..models.post import Post
from ..models.photo import Photo
from ..models.reward import Reward
from ..models.user import User
from ..schemas.post_schema import PostStatus
from typing import Optional, List
from datetime import datetime


class PostRepository:
    """Repository layer for post operations"""
    
    def __init__(self, db: Session):
        self.db = db
    

    
    def create_post(self, builder) -> Optional[Post]:
        """
        Create a new post from builder using getter methods
        
        This method uses builder's getter methods for cleaner access
        and always creates reward records (even with 0 points).
        """
        try:
            # Create the main post entity using builder getter methods
            new_post = Post(
                owner_id=builder.get_owner_id(),
                pet_name=builder.get_pet_name(),
                pet_spec=builder.get_pet_species(),  # Uses mapped field from builder
                pet_breed=builder.get_pet_breed(),
                last_seen_location=builder.get_last_seen_location(),
                contact_information=builder.get_contact_information(),
                description=builder.get_description(),
                status=builder.get_status()
            )
            self.db.add(new_post)
            self.db.flush()  # Get the post ID for related entities
            
            # Create photos using builder getter methods
            for photo_url in builder.get_photos():
                photo = Photo(
                    post_id=new_post.id,
                    photo_url=photo_url
                )
                self.db.add(photo)
            
            # Always create reward record (even with 0 points) using builder getters
            reward = Reward(
                post_id=new_post.id,
                amount=builder.get_reward_amount(),  # Use getter method
                status=builder.get_reward_status()   # Use getter method
            )
            self.db.add(reward)
            
            self.db.commit()
            
            # Return the complete post with relationships
            return self.get_post_by_id(new_post.id)
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """Get a post by ID with all related data including notifications"""
        return (
            self.db.query(Post)
            .options(
                joinedload(Post.owner),
                joinedload(Post.photos),
                joinedload(Post.rewards),
                joinedload(Post.notifications)
            )
            .filter(Post.id == post_id)
            .first()
        )
    
    def get_posts(self, status: Optional[str] = None, user_id: Optional[int] = None) -> List[Post]:
        """Get posts with optional filtering including notifications"""
        query = (
            self.db.query(Post)
            .options(
                joinedload(Post.owner),
                joinedload(Post.photos),
                joinedload(Post.rewards),
                joinedload(Post.notifications)
            )
        )
        
        # Apply filters
        filters = []
        if status:
            filters.append(Post.status == status)
        if user_id:
            filters.append(Post.owner_id == user_id)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.order_by(Post.created_at.desc()).all()
    
    def update_post_status(self, post_id: int, status: str, owner_id: Optional[int] = None) -> Optional[Post]:
        """Update post status (optionally check ownership)"""
        try:
            query = self.db.query(Post).filter(Post.id == post_id)
            
            # If owner_id is provided, ensure only the owner can update
            if owner_id is not None:
                query = query.filter(Post.owner_id == owner_id)
            
            post = query.first()
            if not post:
                return None
            
            post.status = status
            post.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Return updated post with relationships
            return self.get_post_by_id(post.id)
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def close_post(self, post_id: int, owner_id: Optional[int] = None) -> Optional[Post]:
        """Close a post (set status to closed)"""
        return self.update_post_status(post_id, "closed", owner_id)
    
    def mark_post_as_found(self, post_id: int, owner_id: Optional[int] = None) -> Optional[Post]:
        """Mark a post as found"""
        return self.update_post_status(post_id, "found", owner_id)
    
    def post_exists(self, post_id: int) -> bool:
        """Check if a post exists"""
        return self.db.query(Post).filter(Post.id == post_id).first() is not None
    
    def is_post_owner(self, post_id: int, user_id: int) -> bool:
        """Check if user is the owner of the post"""
        post = self.db.query(Post).filter(
            Post.id == post_id, 
            Post.owner_id == user_id
        ).first()
        return post is not None
    
    def get_posts_count(self, status: Optional[str] = None, user_id: Optional[int] = None) -> int:
        """Get total count of posts with optional filtering"""
        query = self.db.query(Post)
        
        filters = []
        if status:
            filters.append(Post.status == status)
        if user_id:
            filters.append(Post.owner_id == user_id)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.count()
