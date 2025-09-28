from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from ..models.post import Post
from ..models.photo import Photo
from ..models.reward import Reward
from ..models.user import User
from ..schemas.post_schema import PostCreate, PostStatus
from typing import Optional, List
from datetime import datetime


class PostRepository:
    """Repository layer for post operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_post(self, post_data: PostCreate, owner_id: int) -> Optional[Post]:
        """Create a new post with photos and reward"""
        try:
            # Create the post
            new_post = Post(
                pet_name=post_data.pet_name,
                pet_spec=post_data.pet_species,  # Map pet_species to pet_spec
                pet_breed=post_data.pet_breed,
                last_seen_location=post_data.last_seen_location,
                contact_information=post_data.contact_information,
                description=post_data.description,
                status="lost",  # Default status
                owner_id=owner_id
            )
            
            self.db.add(new_post)
            self.db.flush()  # Get the post ID
            
            # Create photos
            for photo_url in post_data.photos:
                photo = Photo(
                    post_id=new_post.id,
                    photo_url=photo_url
                )
                self.db.add(photo)
            
            # Create reward if points > 0
            if post_data.reward_points and post_data.reward_points > 0:
                reward = Reward(
                    post_id=new_post.id,
                    amount=post_data.reward_points  # Map reward_points to amount
                )
                self.db.add(reward)
            
            self.db.commit()
            
            # Return the complete post with relationships
            return self.get_post_by_id(new_post.id)
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """Get a post by ID with all related data"""
        return (
            self.db.query(Post)
            .options(
                joinedload(Post.owner),
                joinedload(Post.photos),
                joinedload(Post.rewards)
            )
            .filter(Post.id == post_id)
            .first()
        )
    
    def get_posts(self, status: Optional[str] = None, user_id: Optional[int] = None) -> List[Post]:
        """Get posts with optional filtering"""
        query = (
            self.db.query(Post)
            .options(
                joinedload(Post.owner),
                joinedload(Post.photos),
                joinedload(Post.rewards)
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
