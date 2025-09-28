from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.report import ReportStatus


class ReportCreateForm(BaseModel):
    """Form data for creating a report"""
    post_id: int = Field(..., description="ID of the post being reported about")
    description: str = Field(..., min_length=1, max_length=2000, description="Description of the report")
    location: Optional[str] = Field(None, max_length=500, description="Location where the pet was found (optional)")

    class Config:
        schema_extra = {
            "example": {
                "post_id": 1,
                "description": "I saw this pet near the park on Main Street",
                "location": "Main Street Park, near the playground"
            }
        }


class ReportPhotoResponse(BaseModel):
    """Response for report photo"""
    id: int
    photo_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Basic user information for reports"""
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Basic post information for reports"""
    id: int
    pet_name: str
    pet_spec: str
    status: str

    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    """Response for report details"""
    id: int
    post_id: int
    reporter_id: int
    description: str
    location: Optional[str]
    status: ReportStatus
    created_at: datetime
    
    # Related data
    reporter: Optional[UserResponse] = None
    post: Optional[PostResponse] = None
    photos: List[ReportPhotoResponse] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_report(cls, report) -> 'ReportResponse':
        """Create ReportResponse from Report model"""
        return cls(
            id=report.id,
            post_id=report.post_id,
            reporter_id=report.reporter_id,
            description=report.description,
            location=report.location,
            status=report.status,
            created_at=report.created_at,
            reporter=UserResponse.model_validate(report.reporter) if report.reporter else None,
            post=PostResponse.model_validate(report.post) if report.post else None,
            photos=[ReportPhotoResponse.model_validate(photo) for photo in report.photos]
        )