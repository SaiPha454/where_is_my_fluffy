"""
Example script demonstrating the password hashing strategy pattern
Run this script to see different algorithms in action
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.password_strategies import BcryptStrategy, PBKDF2Strategy, SHA256Strategy
from app.utils.auth_utils import PasswordHelper
from app.config.password_config import PasswordConfig


def demonstrate_strategies():
    """Demonstrate different password hashing strategies"""
    test_password = "MySecretPassword123!"
    
    print("=== Password Hashing Strategy Pattern Demo ===\n")
    
    # Test each strategy individually
    strategies = [
        ("Bcrypt (12 rounds)", BcryptStrategy(rounds=12)),
        ("Bcrypt (8 rounds)", BcryptStrategy(rounds=8)),
        ("PBKDF2 (100,000 iterations)", PBKDF2Strategy(iterations=100000)),
        ("PBKDF2 (50,000 iterations)", PBKDF2Strategy(iterations=50000)),
        ("SHA256 (Not for production!)", SHA256Strategy()),
    ]
    
    for name, strategy in strategies:
        print(f"--- {name} ---")
        print(f"Algorithm: {strategy.get_algorithm_name()}")
        
        # Hash the password
        hashed = strategy.hash_password(test_password)
        print(f"Hashed: {hashed[:50]}..." if len(hashed) > 50 else f"Hashed: {hashed}")
        
        # Verify the password
        is_valid = strategy.verify_password(test_password, hashed)
        print(f"Verification: {'✓ Valid' if is_valid else '✗ Invalid'}")
        
        # Test with wrong password
        is_invalid = strategy.verify_password("WrongPassword", hashed)
        print(f"Wrong password test: {'✗ Should be invalid!' if is_invalid else '✓ Correctly rejected'}")
        
        print()


def demonstrate_password_helper():
    """Demonstrate PasswordHelper with different algorithms"""
    test_password = "AnotherTestPassword456!"
    
    print("=== PasswordHelper with Different Algorithms ===\n")
    
    algorithms = [
        ("bcrypt", {"rounds": 10}),
        ("pbkdf2", {"iterations": 80000}),
        ("sha256", {}),
    ]
    
    for algorithm, kwargs in algorithms:
        print(f"--- Using {algorithm.upper()} ---")
        
        try:
            helper = PasswordHelper.create_with_algorithm(algorithm, **kwargs)
            print(f"Algorithm info: {helper.get_algorithm_info()}")
            
            # Hash password
            hashed = helper.hash_password(test_password)
            print(f"Hashed: {hashed[:50]}..." if len(hashed) > 50 else f"Hashed: {hashed}")
            
            # Verify password
            is_valid = helper.verify_password(test_password, hashed)
            print(f"Verification: {'✓ Valid' if is_valid else '✗ Invalid'}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print()


def demonstrate_config():
    """Demonstrate configuration-based password helper"""
    print("=== Configuration-Based Password Helper ===\n")
    
    # Show current config
    config_info = PasswordConfig.get_current_config_info()
    print(f"Current configuration:")
    print(f"  Algorithm: {config_info['algorithm']}")
    print(f"  Settings: {config_info['settings']}")
    print(f"  Source: {config_info['algorithm_source']}")
    print()
    
    # Create helper using config
    helper = PasswordConfig.create_password_helper()
    print(f"Created helper with algorithm: {helper.get_algorithm_info()}")
    
    # Test password
    test_password = "ConfigTestPassword789!"
    hashed = helper.hash_password(test_password)
    is_valid = helper.verify_password(test_password, hashed)
    
    print(f"Password hashed and verified: {'✓ Success' if is_valid else '✗ Failed'}")
    print()
    
    print("To change algorithm, set environment variable:")
    print("  export PASSWORD_ALGORITHM=pbkdf2")
    print("  export PBKDF2_ITERATIONS=150000")
    print("or")
    print("  export PASSWORD_ALGORITHM=bcrypt")
    print("  export BCRYPT_ROUNDS=14")


if __name__ == "__main__":
    print("🔐 Password Hashing Strategy Pattern Demonstration\n")
    
    try:
        demonstrate_strategies()
        demonstrate_password_helper()
        demonstrate_config()
        
        print("\n=== Demo completed successfully! ===")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()