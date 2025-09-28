from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL for SQLite
DATABASE_URL = "sqlite:///./myfluffy.db"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=True  # Set to False in production to reduce logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def create_tables():
    """Create all database tables"""
    # Import all models to ensure they're registered with Base
    from ..models.user import User
    from ..models.post import Post
    from ..models.photo import Photo
    from ..models.report import Report
    from ..models.report_photo import ReportPhoto
    from ..models.notification import Notification
    from ..models.reward import Reward
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

# Function to drop all tables (useful for development)
def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)
    print("🗑️ Database tables dropped!")

# Function to reset database (drop and create)
def reset_database():
    """Reset database by dropping and creating all tables"""
    drop_tables()
    create_tables()
    print("🔄 Database reset completed!")