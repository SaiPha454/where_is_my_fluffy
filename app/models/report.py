from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
from ..db.database import Base


class ReportStatus(enum.Enum):
    pending = "pending"
    rewarded = "rewarded"
    rejected = "rejected"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("Post", back_populates="reports")
    reporter = relationship("User", back_populates="reports")
    notifications = relationship("Notification", back_populates="report", cascade="all, delete-orphan")