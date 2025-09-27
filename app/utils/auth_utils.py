import bcrypt
import secrets
from typing import Dict, Any
import uuid


class PasswordHelper:
    """Utility class for password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)


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