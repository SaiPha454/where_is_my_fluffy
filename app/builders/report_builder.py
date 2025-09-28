from ..models.report import ReportStatus
from typing import List, Optional


class ReportBuilder:
    """
    Builder for creating Report entities with individual setter methods.
    
    Provides clean API for constructing reports with validation,
    field mapping, and proper defaults.
    """
    
    def __init__(self):
        # Core fields
        self._post_id: Optional[int] = None
        self._reporter_id: Optional[int] = None
        self._description: Optional[str] = None
        self._location: Optional[str] = None
        self._photos: List[str] = []
        self._status: ReportStatus = ReportStatus.pending  # Always pending for new reports
    
    # Individual setter methods (as requested)
    def set_post_id(self, post_id: int) -> 'ReportBuilder':
        """Set the post ID this report is about"""
        if not isinstance(post_id, int) or post_id <= 0:
            raise ValueError("Post ID must be a positive integer")
        self._post_id = post_id
        return self
    
    def set_reporter_id(self, reporter_id: int) -> 'ReportBuilder':
        """Set the ID of the user making the report"""
        if not isinstance(reporter_id, int) or reporter_id <= 0:
            raise ValueError("Reporter ID must be a positive integer")
        self._reporter_id = reporter_id
        return self
    
    def set_description(self, description: str) -> 'ReportBuilder':
        """Set the report description (required)"""
        if not description or not description.strip():
            raise ValueError("Description is required and cannot be empty")
        self._description = description.strip()
        return self
    
    def set_location(self, location: Optional[str] = None) -> 'ReportBuilder':
        """Set the location where the pet was found (optional)"""
        self._location = location.strip() if location else None
        return self
    
    def set_photos(self, photos: List[str]) -> 'ReportBuilder':
        """Set the list of photo URLs (optional, max 4)"""
        if photos and len(photos) > 4:
            raise ValueError("Maximum 4 photos allowed per report")
        self._photos = photos if photos else []
        return self
    
    def set_status(self, status: ReportStatus) -> 'ReportBuilder':
        """Set report status (defaults to pending, mainly for testing)"""
        if not isinstance(status, ReportStatus):
            raise ValueError("Status must be a valid ReportStatus enum")
        self._status = status
        return self
    
    # Getter methods for repository access
    def get_post_id(self) -> int:
        """Get the post ID"""
        if self._post_id is None:
            raise ValueError("Post ID is required")
        return self._post_id
    
    def get_reporter_id(self) -> int:
        """Get the reporter ID"""
        if self._reporter_id is None:
            raise ValueError("Reporter ID is required")
        return self._reporter_id
    
    def get_description(self) -> str:
        """Get the report description"""
        if self._description is None:
            raise ValueError("Description is required")
        return self._description
    
    def get_location(self) -> Optional[str]:
        """Get the location (can be None)"""
        return self._location
    
    def get_photos(self) -> List[str]:
        """Get the list of photo URLs"""
        return self._photos.copy()  # Return copy to prevent external modification
    
    def get_status(self) -> ReportStatus:
        """Get the report status (always pending for new reports)"""
        return self._status
    
    # Validation method
    def validate(self) -> None:
        """Validate all required fields are set"""
        if self._post_id is None:
            raise ValueError("Post ID is required")
        if self._reporter_id is None:
            raise ValueError("Reporter ID is required")
        if not self._description:
            raise ValueError("Description is required")
        if self._photos and len(self._photos) > 4:
            raise ValueError("Maximum 4 photos allowed per report")
    
    # Build method for creating the final object (if needed)
    def build(self) -> dict:
        """Build and return report data as dictionary (mainly for testing)"""
        self.validate()
        return {
            'post_id': self._post_id,
            'reporter_id': self._reporter_id,
            'description': self._description,
            'location': self._location,
            'photos': self._photos.copy(),
            'status': self._status
        }