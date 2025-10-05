from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from fastapi import Form, UploadFile


# Forward declaration to avoid circular imports
class NotificationResponse(BaseModel):
    """Notification information in post responses"""
    id: int
    post_id: int
    report_id: int
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PostStatus(str, Enum):
    LOST = "lost"
    FOUND = "found"
    CLOSED = "closed"


class PostCreateForm(BaseModel):
    """Schema for creating a new post via form data"""
    pet_name: str
    pet_species: str
    pet_breed: Optional[str] = None
    last_seen_location: str
    contact_information: str
    description: Optional[str] = None
    reward_points: int = 0
    
    @classmethod
    def as_form(
        cls,
        pet_name: str = Form(..., min_length=1, max_length=100, description="Name of the pet"),
        pet_species: str = Form(..., min_length=1, max_length=50, description="Species of the pet (e.g., Dog, Cat)"),
        pet_breed: Optional[str] = Form(None, max_length=100, description="Breed of the pet"),
        last_seen_location: str = Form(..., min_length=1, max_length=500, description="Last known location of the pet"),
        contact_information: str = Form(..., min_length=1, max_length=500, description="Contact information for the owner"),
        description: Optional[str] = Form(None, max_length=2000, description="Additional description about the pet"),
        reward_points: int = Form(0, ge=0, description="Reward points offered (default: 0)")
    ):
        return cls(
            pet_name=pet_name,
            pet_species=pet_species,
            pet_breed=pet_breed,
            last_seen_location=last_seen_location,
            contact_information=contact_information,
            description=description,
            reward_points=reward_points
        )


class PostCreate(BaseModel):
    """Schema for creating a new post (internal use)"""
    pet_name: str = Field(..., min_length=1, max_length=100, description="Name of the pet")
    pet_species: str = Field(..., min_length=1, max_length=50, description="Species of the pet (e.g., Dog, Cat)")
    pet_breed: Optional[str] = Field(None, max_length=100, description="Breed of the pet")
    last_seen_location: str = Field(..., min_length=1, max_length=500, description="Last known location of the pet")
    contact_information: str = Field(..., min_length=1, max_length=500, description="Contact information for the owner")
    description: Optional[str] = Field(None, max_length=2000, description="Additional description about the pet")
    photos: List[str] = Field(..., min_items=1, max_items=4, description="List of photo paths (1-4 photos required)")
    reward_points: Optional[int] = Field(0, ge=0, description="Reward points offered (default: 0)")
    
    @validator('photos')
    def validate_photos(cls, v):
        if not v or len(v) < 1:
            raise ValueError('At least 1 photo is required')
        if len(v) > 4:
            raise ValueError('Maximum 4 photos allowed')
        return v


class PostStatusUpdate(BaseModel):
    """Schema for updating post status"""
    status: PostStatus


class UserResponse(BaseModel):
    """User information in post responses"""
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True


class PhotoResponse(BaseModel):
    """Photo information in post responses"""
    id: int
    photo_url: str
    uploaded_at: datetime
    
    @classmethod
    def from_photo(cls, photo):
        """Create PhotoResponse from Photo model"""
        return cls(
            id=photo.id,
            photo_url=photo.photo_url,
            uploaded_at=photo.created_at  # Map created_at to uploaded_at
        )
    
    class Config:
        from_attributes = True


class RewardResponse(BaseModel):
    """Reward information in post responses"""
    id: int
    points: int
    is_claimed: bool
    created_at: datetime
    claimed_at: Optional[datetime] = None
    
    @classmethod
    def from_reward(cls, reward):
        """Create RewardResponse from Reward model"""
        return cls(
            id=reward.id,
            points=reward.amount,  # Map amount to points
            is_claimed=(reward.status.value == "completed"),  # Map status to is_claimed
            created_at=reward.created_at,
            claimed_at=None  # No claimed_at in current model
        )
    
    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Schema for post responses"""
    id: int
    pet_name: str
    pet_species: str
    pet_breed: Optional[str]
    last_seen_location: str
    contact_information: str
    description: Optional[str]
    status: PostStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related information
    owner: UserResponse
    photos: List[PhotoResponse]
    reward: Optional[RewardResponse]
    notifications: List[NotificationResponse] = []
    
    @classmethod
    def from_post(cls, post, include_notifications=True):
        """Create PostResponse from Post model with proper field mapping"""
        notifications = []
        if include_notifications and hasattr(post, 'notifications'):
            # Filter for unread notifications only
            unread_notifications = [n for n in post.notifications if not n.is_read]
            notifications = [NotificationResponse.model_validate(notification) for notification in unread_notifications]
        
        return cls(
            id=post.id,
            pet_name=post.pet_name,
            pet_species=post.pet_spec,  # Map pet_spec to pet_species
            pet_breed=post.pet_breed,
            last_seen_location=post.last_seen_location,
            contact_information=post.contact_information,
            description=post.description,
            status=post.status.value,
            created_at=post.created_at,
            updated_at=None,  # No updated_at in current model
            owner=UserResponse(
                id=post.owner.id,
                username=post.owner.username,
                email=post.owner.email
            ),
            photos=[PhotoResponse.from_photo(photo) for photo in post.photos],
            reward=RewardResponse.from_reward(post.rewards[0]) if post.rewards else None,
            notifications=notifications
        )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "pet_name": "Buddy",
                "pet_species": "Dog",
                "pet_breed": "Golden Retriever",
                "last_seen_location": "Central Park, New York",
                "contact_information": "Phone: 555-0123, Email: john@example.com",
                "description": "Friendly golden retriever, responds to 'Buddy'. Has a red collar.",
                "status": "lost",
                "created_at": "2025-09-28T10:30:00",
                "updated_at": None,
                "owner": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com"
                },
                "photos": [
                    {
                        "id": 1,
                        "photo_url": "https://example.com/photo1.jpg",
                        "uploaded_at": "2025-09-28T10:30:00"
                    }
                ],
                "reward": {
                    "id": 1,
                    "points": 100,
                    "is_claimed": False,
                    "created_at": "2025-09-28T10:30:00",
                    "claimed_at": None
                },
                "notifications": [
                    {
                        "id": 10,
                        "post_id": 1,
                        "report_id": 5,
                        "message": "New report on your post",
                        "is_read": False,
                        "created_at": "2025-10-03T10:30:00"
                    }
                ]
            }
        }


class PostListResponse(BaseModel):
    """Schema for listing posts with pagination info"""
    posts: List[PostResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "posts": [
                    {
                        "id": 1,
                        "pet_name": "Buddy",
                        "pet_species": "Dog",
                        "pet_breed": "Golden Retriever",
                        "last_seen_location": "Central Park, New York",
                        "contact_information": "Phone: 555-0123, Email: john@example.com",
                        "description": "Friendly golden retriever, responds to 'Buddy'. Has a red collar.",
                        "status": "lost",
                        "created_at": "2025-09-28T10:30:00",
                        "updated_at": None,
                        "owner": {
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com"
                        },
                        "photos": [
                            {
                                "id": 1,
                                "photo_url": "https://example.com/photo1.jpg",
                                "uploaded_at": "2025-09-28T10:30:00"
                            }
                        ],
                        "reward": {
                            "id": 1,
                            "points": 100,
                            "is_claimed": False,
                            "created_at": "2025-09-28T10:30:00",
                            "claimed_at": None
                        },
                        "notifications": [
                            {
                                "id": 10,
                                "post_id": 1,
                                "report_id": 5,
                                "message": "New report on your post",
                                "is_read": False,
                                "created_at": "2025-10-03T10:30:00"
                            }
                        ]
                    }
                ],
                "total": 25
            }
        }


# Query parameter models for filtering
class PostFilters(BaseModel):
    """Query parameters for filtering posts"""
    status: Optional[PostStatus] = None
    user_id: Optional[int] = None