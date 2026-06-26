from sqlalchemy import Column, Integer, String, Enum, DateTime
from datetime import datetime
import enum
from app.db.base import Base

class JobState(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True, nullable=True)
    file_path = Column(String, nullable=True)
    state = Column(Enum(JobState), default=JobState.PENDING, index=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
