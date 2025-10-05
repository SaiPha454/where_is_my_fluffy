from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..schemas.auth_schema import UserResponse
from ..schemas.user_schema import PublicUserResponse, BalanceTopUpRequest
from ..routers.auth_route import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get UserService instance"""
    user_repository = UserRepository(db)
    return UserService(user_repository)


@router.get("/{user_id}", response_model=PublicUserResponse, responses={
    404: {
        "description": "User not found",
        "content": {
            "application/json": {
                "example": {"detail": "User with id 123 not found"}
            }
        }
    },
    500: {
        "description": "Server error while retrieving user",
        "content": {
            "application/json": {
                "example": {"detail": "Error retrieving user: <reason>"}
            }
        }
    }
})
def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Get public user profile by ID
    
    Returns user information excluding sensitive data like balance and password_hash.
    This endpoint is public and doesn't require authentication.
    Only shows: id, username, email, created_at
    """
    return user_service.get_user_by_id(user_id)


@router.put("", response_model=UserResponse, status_code=status.HTTP_200_OK, responses={
    401: {
        "content": {
            "application/json": {
                "examples": {
                    "MissingSession": {
                        "summary": "Missing session cookie",
                        "value": {"detail": "Authentication required"}
                    },
                    "InvalidSession": {
                        "summary": "Invalid or expired session",
                        "value": {"detail": "Invalid or expired session"}
                    }
                }
            }
        }
    },
    404: {
        "description": "User not found",
        "content": {
            "application/json": {
                "example": {"detail": "User not found"}
            }
        }
    },
    400: {
        "description": "Failed to update balance",
        "content": {
            "application/json": {
                "example": {"detail": "Failed to update balance"}
            }
        }
    },
    500: {
        "description": "Server error while updating balance",
        "content": {
            "application/json": {
                "example": {"detail": "Error updating balance: <reason>"}
            }
        }
    }
})
def top_up_balance(
    top_up_request: BalanceTopUpRequest,
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Top up the balance of the current authenticated user
    
    - **amount**: Positive amount to add to current balance
    
    The new balance will be: current_balance + amount
    """
    return user_service.top_up_balance(current_user.id, top_up_request)