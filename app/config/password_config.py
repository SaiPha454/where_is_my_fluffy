"""
Configuration for password hashing strategies
"""
import os
from typing import Dict, Any, Optional
from ..utils.auth_utils import PasswordHelper


class PasswordConfig:
    """Configuration class for password hashing settings"""
    
    # Default settings for each algorithm
    DEFAULT_SETTINGS = {
        'bcrypt': {
            'rounds': 12
        },
        'pbkdf2': {
            'iterations': 100000
        },
        'sha256': {
            # No additional settings for SHA256 (not recommended for production)
        }
    }
    
    @classmethod
    def get_algorithm(cls) -> str:
        """Get the password hashing algorithm from environment or default to bcrypt"""
        return os.getenv('PASSWORD_ALGORITHM', 'bcrypt').lower()
    
    @classmethod
    def get_algorithm_settings(cls, algorithm: Optional[str] = None) -> Dict[str, Any]:
        """Get settings for the specified algorithm"""
        if algorithm is None:
            algorithm = cls.get_algorithm()
        
        # Get default settings
        settings = cls.DEFAULT_SETTINGS.get(algorithm, {}).copy()
        
        # Override with environment variables if available
        if algorithm == 'bcrypt':
            env_rounds = os.getenv('BCRYPT_ROUNDS')
            if env_rounds and env_rounds.isdigit():
                settings['rounds'] = int(env_rounds)
        
        elif algorithm == 'pbkdf2':
            env_iterations = os.getenv('PBKDF2_ITERATIONS')
            if env_iterations and env_iterations.isdigit():
                settings['iterations'] = int(env_iterations)
        
        return settings
    
    @classmethod
    def create_password_helper(cls) -> PasswordHelper:
        """Create a PasswordHelper instance with configured algorithm and settings"""
        algorithm = cls.get_algorithm()
        settings = cls.get_algorithm_settings(algorithm)
        
        try:
            return PasswordHelper.create_with_algorithm(algorithm, **settings)
        except ValueError as e:
            # Fallback to bcrypt if invalid algorithm specified
            print(f"Warning: {e}. Falling back to bcrypt.")
            return PasswordHelper.create_with_algorithm('bcrypt', **cls.DEFAULT_SETTINGS['bcrypt'])
    
    @classmethod
    def get_current_config_info(cls) -> Dict[str, Any]:
        """Get current configuration information for logging/debugging"""
        algorithm = cls.get_algorithm()
        settings = cls.get_algorithm_settings(algorithm)
        
        return {
            'algorithm': algorithm,
            'settings': settings,
            'algorithm_source': 'environment' if os.getenv('PASSWORD_ALGORITHM') else 'default'
        }