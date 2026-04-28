import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum
from core.database import Base
import enum


class JobType(str, enum.Enum):
    WORD_STATS = "WORD_STATS"
    WORD_STATS_COMPARE = "WORD_STATS_COMPARE"


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    DONE = "DONE"
    FAILED = "FAILED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)
    status = Column(String, nullable=False, default=JobStatus.PENDING)
    payload = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
