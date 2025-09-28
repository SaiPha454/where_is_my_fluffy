from sqlalchemy.orm import Session
from ..models.user import User
from typing import Optional


class UserRepository:
    """Repository layer for user operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user_balance(self, user_id: int, new_balance: int) -> Optional[User]:
        """Update user balance"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            user.balance = new_balance
            self.db.commit()
            
            # Return the updated user
            return user
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def user_exists(self, user_id: int) -> bool:
        """Check if a user exists"""
        return self.db.query(User).filter(User.id == user_id).first() is not None