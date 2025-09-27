from sqlalchemy.orm import Session
from ..repositories.auth_repository import AuthRepository
from ..schemas.auth_schema import UserRegistrationRequest, UserLoginRequest, AuthResponse, UserResponse
from ..utils.auth_utils import SessionManager
from typing import Tuple, Optional


class AuthService:
    """Service layer for authentication business logic"""
    
    def __init__(self, db: Session):
        self.auth_repo = AuthRepository(db)
    
    def register_user(self, registration_data: UserRegistrationRequest) -> Tuple[AuthResponse, Optional[str]]:
        """Register a new user and create session"""
        try:
            # Check if email already exists
            if self.auth_repo.email_exists(registration_data.email):
                return (
                    AuthResponse(
                        success=False,
                        message="Email already registered",
                        user=None
                    ),
                    None
                )
            
            # Create the user
            new_user = self.auth_repo.create_user(
                username=registration_data.username,
                email=registration_data.email,
                password=registration_data.password
            )
            
            if not new_user:
                return (
                    AuthResponse(
                        success=False,
                        message="Failed to create user",
                        user=None
                    ),
                    None
                )
            
            # Create session for the new user (auto-login after registration)
            session_id = SessionManager.create_session(
                user_id=new_user.id,
                username=new_user.username,
                email=new_user.email
            )
            
            # Return success response
            user_response = UserResponse.model_validate(new_user)
            auth_response = AuthResponse(
                success=True,
                message="User registered successfully",
                user=user_response
            )
            
            return auth_response, session_id
            
        except Exception as e:
            return (
                AuthResponse(
                    success=False,
                    message=f"Registration failed: {str(e)}",
                    user=None
                ),
                None
            )
    
    def login_user(self, login_data: UserLoginRequest) -> Tuple[AuthResponse, Optional[str]]:
        """Login user and create session"""
        try:
            # Verify credentials
            user = self.auth_repo.verify_user_credentials(
                email=login_data.email,
                password=login_data.password
            )
            
            if not user:
                return (
                    AuthResponse(
                        success=False,
                        message="Invalid email or password",
                        user=None
                    ),
                    None
                )
            
            # Create session
            session_id = SessionManager.create_session(
                user_id=user.id,
                username=user.username,
                email=user.email
            )
            
            # Return success response
            user_response = UserResponse.model_validate(user)
            auth_response = AuthResponse(
                success=True,
                message="Login successful",
                user=user_response
            )
            
            return auth_response, session_id
            
        except Exception as e:
            return (
                AuthResponse(
                    success=False,
                    message=f"Login failed: {str(e)}",
                    user=None
                ),
                None
            )
    
    def logout_user(self, session_id: str) -> AuthResponse:
        """Logout user by deleting session"""
        try:
            success = SessionManager.delete_session(session_id)
            
            if success:
                return AuthResponse(
                    success=True,
                    message="Logout successful",
                    user=None
                )
            else:
                return AuthResponse(
                    success=False,
                    message="Invalid session",
                    user=None
                )
                
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Logout failed: {str(e)}",
                user=None
            )
    
    def get_current_user(self, session_id: str) -> Optional[UserResponse]:
        """Get current user from session"""
        try:
            session_data = SessionManager.get_user_from_session(session_id)
            if not session_data:
                return None
            
            # Get fresh user data from database
            user = self.auth_repo.get_user_by_id(session_data["user_id"])
            if not user:
                return None
            
            return UserResponse.model_validate(user)
            
        except Exception:
            return None