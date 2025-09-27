import os
from typing import Literal

# Configuration settings
class Config:
    """Application configuration"""
    
    # Password hashing configuration
    PASSWORD_ALGORITHM: Literal["bcrypt", "argon2"] = os.getenv("PASSWORD_ALGORITHM", "bcrypt")
    
    # Bcrypt configuration
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    # Argon2 configuration  
    ARGON2_TIME_COST: int = int(os.getenv("ARGON2_TIME_COST", "2"))
    ARGON2_MEMORY_COST: int = int(os.getenv("ARGON2_MEMORY_COST", "102400"))  # 100 MB in KiB
    ARGON2_PARALLELISM: int = int(os.getenv("ARGON2_PARALLELISM", "8"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./myfluffy.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    @classmethod
    def get_password_helper_config(cls):
        """Get password helper configuration based on selected algorithm"""
        if cls.PASSWORD_ALGORITHM == "bcrypt":
            return {
                "algorithm": "bcrypt",
                "rounds": cls.BCRYPT_ROUNDS
            }
        elif cls.PASSWORD_ALGORITHM == "argon2":
            return {
                "algorithm": "argon2", 
                "time_cost": cls.ARGON2_TIME_COST,
                "memory_cost": cls.ARGON2_MEMORY_COST,
                "parallelism": cls.ARGON2_PARALLELISM
            }
        else:
            raise ValueError(f"Unsupported password algorithm: {cls.PASSWORD_ALGORITHM}")