from ..repositories.user_repository import UserRepository
from ..schemas.auth_schema import UserResponse
from ..schemas.user_schema import PublicUserResponse, BalanceTopUpRequest
from fastapi import HTTPException, status


class UserService:
    """Service layer for user operations"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def get_user_by_id(self, user_id: int) -> UserResponse:
        """Get a specific user by ID"""
        try:
            user = self.user_repository.get_user_by_id(user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found"
                )
            
            return UserResponse.model_validate(user)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user: {str(e)}"
            )
    
    def top_up_balance(self, user_id: int, top_up_request: BalanceTopUpRequest) -> UserResponse:
        """Top up the balance of the authenticated user"""
        try:
            # Get current user to check existence and get current balance
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Calculate new balance (add the top-up amount)
            new_balance = user.balance + top_up_request.amount
            
            # Update user balance
            updated_user = self.user_repository.update_user_balance(user_id, new_balance)
            
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update balance"
                )
            
            return UserResponse.model_validate(updated_user)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating balance: {str(e)}"
            )