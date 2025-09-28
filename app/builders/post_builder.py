from typing import List, Dict, Any, Optional
from ..models.post import PostStatus
from ..models.reward import RewardStatus


class PostBuilder:
    """
    Builder pattern for creating posts with centralized creation logic.
    
    This builder handles:
    - Field mapping (pet_species -> pet_spec, reward_points -> amount)
    - Default value assignment
    - Validation rules
    - Conditional entity creation (rewards only when points > 0)
    - Individual property methods (as requested)
    """
    
    def __init__(self):
        # Initialize all properties with consistent structure
        self._post_data = {}
        self._photos = []
        self._reward_data = None
    
    def set_owner_id(self, owner_id: int):
        """Set the post owner ID"""
        self._post_data['owner_id'] = owner_id
        return self
    
    def set_pet_name(self, name: str):
        """Set pet name"""
        self._post_data['pet_name'] = name
        return self
    
    def set_pet_species(self, species: str):
        """Set pet species with field mapping (accepts any string)"""
        self._post_data['pet_spec'] = species  # Field mapping: pet_species → pet_spec
        return self
    
    def set_pet_breed(self, breed: Optional[str] = None):
        """Set pet breed with default handling"""
        self._post_data['pet_breed'] = breed or "Unknown"
        return self
    
    def set_last_seen_location(self, location: str):
        """Set last seen location"""
        self._post_data['last_seen_location'] = location
        return self
    
    def set_contact_information(self, contact: str):
        """Set contact information"""
        self._post_data['contact_information'] = contact
        return self
    
    def set_description(self, description: Optional[str] = None):
        """Set description with intelligent default if None"""
        if description:
            self._post_data['description'] = description
        else:
            # Generate helpful default description
            pet_name = self._post_data.get('pet_name', 'Unknown pet')
            self._post_data['description'] = f"Lost pet named {pet_name}. Please contact if found."
        return self
    
    def set_photos(self, photo_paths: List[str]):
        """Set photo paths with validation"""
        if not photo_paths or len(photo_paths) < 1:
            raise ValueError("At least 1 photo is required")
        if len(photo_paths) > 4:
            raise ValueError("Maximum 4 photos allowed")
        
        self._photos = photo_paths
        return self
    
    def set_reward_points(self, points: int = 0):
        """Set reward points - always creates reward record with pending status"""
        # Always create reward data with pending status regardless of amount
        self._reward_data = {
            'amount': max(0, points),  # Ensure non-negative
            'status': RewardStatus.pending  # Always pending for new posts
        }
        return self
    
    def set_status(self, status: PostStatus = PostStatus.lost):
        """Set post status using PostStatus enum"""
        self._post_data['status'] = status
        return self
    
    # Getter methods for accessing all data (consistent API)
    def get_owner_id(self) -> int:
        """Get the post owner ID"""
        return self._post_data.get('owner_id')
    
    def get_pet_name(self) -> str:
        """Get pet name"""
        return self._post_data.get('pet_name', '')
    
    def get_pet_species(self) -> str:
        """Get pet species (returns mapped field value)"""
        return self._post_data.get('pet_spec', '')
    
    def get_pet_breed(self) -> str:
        """Get pet breed"""
        return self._post_data.get('pet_breed', 'Unknown')
    
    def get_last_seen_location(self) -> str:
        """Get last seen location"""
        return self._post_data.get('last_seen_location', '')
    
    def get_contact_information(self) -> str:
        """Get contact information"""
        return self._post_data.get('contact_information', '')
    
    def get_description(self) -> str:
        """Get description"""
        return self._post_data.get('description', '')
    
    def get_status(self) -> PostStatus:
        """Get post status - returns PostStatus enum"""
        status_str = self._post_data.get('status', 'lost')
        # Convert string to enum if needed
        if isinstance(status_str, str):
            return PostStatus(status_str)
        return status_str
    
    def get_photos(self) -> List[str]:
        """Get photo paths"""
        return self._photos.copy()  # Return copy to prevent external modification
    
    def get_photos_count(self) -> int:
        """Get number of photos"""
        return len(self._photos)
    
    # Getter methods for accessing reward data (always available)
    def get_reward_amount(self) -> int:
        """Get reward amount - always returns an amount (0 or more)"""
        return self._reward_data.get('amount', 0) if self._reward_data else 0
    
    def get_reward_status(self) -> RewardStatus:
        """Get reward status - always returns pending for new posts"""
        if self._reward_data:
            return self._reward_data.get('status', RewardStatus.pending)
        # Default to pending for new posts
        return RewardStatus.pending
    
    def has_reward(self) -> bool:
        """Check if this post has a meaningful reward (> 0 points)"""
        return self.get_reward_amount() > 0
    
    def build(self) -> Dict[str, Any]:
        """
        Build and validate the complete post structure.
        
        Returns:
            Dictionary with all entities ready for persistence:
            - post_data: Main post entity data
            - photos: List of photo paths  
            - reward_data: Reward data (if applicable)
        """
        # Validation
        self._validate()
        
        # Set default status if not already set
        if 'status' not in self._post_data:
            self._post_data['status'] = PostStatus.lost
        
        return {
            'post_data': self._post_data,
            'photos': self._photos,
            'reward_data': self._reward_data  # Always include reward data (even 0 points)
        }
    
    def _validate(self):
        """Validate builder state before building"""
        required_fields = ['owner_id', 'pet_name', 'pet_spec', 'last_seen_location', 'contact_information']
        
        for field in required_fields:
            if field not in self._post_data:
                field_display = 'pet_species' if field == 'pet_spec' else field
                raise ValueError(f"Required field '{field_display}' is missing")
        
        if not self._photos:
            raise ValueError("At least 1 photo is required")
        
        # Ensure reward data exists (should always be set by set_reward_points)
        if self._reward_data is None:
            raise ValueError("Reward data must be set (use set_reward_points, even with 0)")