from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.user import User
from ..utils.auth_utils import PasswordHelper
from typing import Optional


class AuthRepository:
    """Repository layer for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Create a new user"""
        try:
            # Hash the password
            hashed_password = PasswordHelper.hash_password(password)
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                balance=0  # Default balance
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            return new_user
            
        except IntegrityError:
            # Email already exists (unique constraint violation)
            self.db.rollback()
            return None
        except Exception as e:
            self.db.rollback()
            raise e
    
    def verify_user_credentials(self, email: str, password: str) -> Optional[User]:
        """Verify user credentials and return user if valid"""
        user = self.get_user_by_email(email)
        
        if user and PasswordHelper.verify_password(password, user.password_hash):
            return user
        
        return None
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.db.query(User).filter(User.email == email).first() is not None