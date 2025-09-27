from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Request schemas
class UserRegistrationRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password (minimum 6 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


# Response schemas
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    balance: int
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com", 
                    "balance": 0,
                    "created_at": "2024-01-01T00:00:00Z"
                }
            }
        }