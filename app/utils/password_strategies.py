from abc import ABC, abstractmethod
import bcrypt
import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordHashingStrategy(ABC):
    """Abstract base class for password hashing strategies"""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a password and return the hashed string"""
        pass
    
    @abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Return the name of the hashing algorithm"""
        pass


class BcryptStrategy(PasswordHashingStrategy):
    """Bcrypt password hashing strategy"""
    
    def __init__(self, rounds: int = 12):
        """Initialize with configurable work factor (rounds)"""
        self.rounds = rounds
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt"""
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def get_algorithm_name(self) -> str:
        return f"bcrypt (rounds: {self.rounds})"


class Argon2Strategy(PasswordHashingStrategy):
    """Argon2 password hashing strategy"""
    
    def __init__(self, time_cost: int = 2, memory_cost: int = 102400, parallelism: int = 8):
        """
        Initialize with configurable parameters:
        - time_cost: Number of iterations
        - memory_cost: Amount of memory used in KiB
        - parallelism: Number of parallel threads
        """
        self.ph = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
        )
    
    def hash_password(self, password: str) -> str:
        """Hash password using Argon2"""
        return self.ph.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password using Argon2"""
        try:
            self.ph.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            return False
    
    def get_algorithm_name(self) -> str:
        return f"Argon2 (time: {self.ph.time_cost}, memory: {self.ph.memory_cost} KiB)"