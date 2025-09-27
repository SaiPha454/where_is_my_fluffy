from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
from ..db.database import Base


class PostStatus(enum.Enum):
    lost = "lost"
    found = "found"
    closed = "closed"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_name = Column(String, nullable=False)
    pet_spec = Column(String, nullable=False)  # species (e.g., Dog, Cat)
    pet_breed = Column(String, nullable=False)
    last_seen_location = Column(String, nullable=False)
    contact_information = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(PostStatus), nullable=False, default=PostStatus.lost)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="posts")
    photos = relationship("Photo", back_populates="post", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="post", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="post", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="post", cascade="all, delete-orphan")