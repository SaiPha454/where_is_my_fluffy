from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..services.auth_service import AuthService
from ..schemas.auth_schema import UserRegistrationRequest, UserLoginRequest, AuthResponse
from ..utils.auth_utils import SessionManager
from typing import Optional

router = APIRouter(tags=["authentication"])


@router.post("/auth/register", response_model=AuthResponse)
async def register_user(
    user_data: UserRegistrationRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    auth_response, session_id = auth_service.register_user(user_data)
    
    if auth_response.success and session_id:
        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,  # Prevent XSS attacks
            secure=False,   # Set to True in production with HTTPS
            samesite="lax"  # CSRF protection
        )
    
    return auth_response


@router.post("/auth/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Login a user"""
    auth_service = AuthService(db)
    auth_response, session_id = auth_service.login_user(login_data)
    
    if auth_response.success and session_id:
        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,  # Prevent XSS attacks
            secure=False,   # Set to True in production with HTTPS
            samesite="lax"  # CSRF protection
        )
    
    return auth_response


@router.post("/auth/logout", response_model=AuthResponse)
async def logout_user(
    response: Response,
    session_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Logout a user"""
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session found"
        )
    
    auth_service = AuthService(db)
    auth_response = auth_service.logout_user(session_id)
    
    if auth_response.success:
        # Clear session cookie
        response.delete_cookie(key="session_id")
    
    return auth_response


# Dependency to get current authenticated user
def get_current_user(
    session_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Dependency to get current authenticated user"""
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    auth_service = AuthService(db)
    current_user = auth_service.get_current_user(session_id)
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return current_user


# Optional: Get current user info endpoint
@router.get("/auth/me", response_model=AuthResponse)
async def get_current_user_info(
    current_user=Depends(get_current_user)
):
    """Get current user information"""
    return AuthResponse(
        success=True,
        message="User information retrieved",
        user=current_user
    )