from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
from ..db.database import Base


class RewardStatus(enum.Enum):
    pending = "pending"
    completed = "completed"


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(Enum(RewardStatus), nullable=False, default=RewardStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("Post", back_populates="rewards")