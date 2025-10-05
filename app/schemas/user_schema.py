from pydantic import BaseModel, Field
from datetime import datetime


class PublicUserResponse(BaseModel):
    """Public user profile response (excludes sensitive data like balance)"""
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class BalanceTopUpRequest(BaseModel):
    """Request schema for topping up user balance"""
    amount: int = Field(..., gt=0, description="Amount to add to balance (must be positive)")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 100
            }
        }