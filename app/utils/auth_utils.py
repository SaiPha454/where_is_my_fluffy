import secrets
from typing import Dict, Any, Optional
import uuid
from .password_strategies import PasswordHashingStrategy, BcryptStrategy, Argon2Strategy


class PasswordHelper:
    """Password utility class using Strategy pattern"""
    
    # Available strategies
    _strategies = {
        'bcrypt': BcryptStrategy,
        'argon2': Argon2Strategy,
    }
    
    def __init__(self, strategy: Optional[PasswordHashingStrategy] = None):
        """Initialize with a specific strategy"""
        self.strategy = strategy or BcryptStrategy()  # Default to bcrypt
    
    @classmethod
    def create_with_algorithm(cls, algorithm: str = 'bcrypt', **kwargs):
        """Factory method to create PasswordHelper with specific algorithm"""
        if algorithm not in cls._strategies:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Available: {list(cls._strategies.keys())}")
        
        strategy_class = cls._strategies[algorithm]
        strategy = strategy_class(**kwargs)
        return cls(strategy)
    
    def hash_password(self, password: str) -> str:
        """Hash a password using the configured strategy"""
        return self.strategy.hash_password(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password using the configured strategy"""
        return self.strategy.verify_password(password, hashed_password)
    
    def get_algorithm_info(self) -> str:
        """Get information about the current algorithm"""
        return self.strategy.get_algorithm_name()
    
    @classmethod
    def get_default_instance(cls):
        """Get default PasswordHelper instance (for backward compatibility)"""
        return cls.create_with_algorithm('bcrypt', rounds=12)
    
    # Static methods for backward compatibility
    @staticmethod
    def hash_password_static(password: str) -> str:
        """Static method for backward compatibility"""
        helper = PasswordHelper.get_default_instance()
        return helper.hash_password(password)
    
    @staticmethod
    def verify_password_static(password: str, hashed_password: str) -> bool:
        """Static method for backward compatibility"""
        helper = PasswordHelper.get_default_instance()
        return helper.verify_password(password, hashed_password)


class SessionManager:
    """Simple in-memory session management"""
    
    # In production, you should use Redis or database for session storage
    _sessions: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def create_session(cls, user_id: int, username: str, email: str) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        cls._sessions[session_id] = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": str(uuid.uuid1().time)
        }
        return session_id
    
    @classmethod
    def get_session(cls, session_id: str) -> Dict[str, Any]:
        """Get session data by session ID"""
        return cls._sessions.get(session_id)
    
    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        """Delete a session"""
        if session_id in cls._sessions:
            del cls._sessions[session_id]
            return True
        return False
    
    @classmethod
    def get_user_from_session(cls, session_id: str) -> Dict[str, Any]:
        """Get user info from session"""
        session_data = cls.get_session(session_id)
        return session_data if session_data else None