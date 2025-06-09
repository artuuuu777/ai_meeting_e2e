from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import MeetingStatus, ProcessingStatus

if TYPE_CHECKING:
    from app.models.insight import Insight
    from app.models.segment import Segment
    from app.models.user import User


class Meeting(Base, TimestampMixin):
    __tablename__ = "meetings"

    # Basic info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Participants
    participants: Mapped[List[str]] = mapped_column(JSON, default=list)
    organizer_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    
    # Status
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus), default=MeetingStatus.SCHEDULED
    )
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    
    # Storage
    s3_audio_uri: Mapped[Optional[str]] = mapped_column(String(500))
    s3_transcript_uri: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Metadata
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Processing timestamps
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    
    # Cost tracking
    processing_cost_usd: Mapped[Optional[float]] = mapped_column(
        default=0.0, nullable=True
    )
    
    # Flags
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    segments: Mapped[List["Segment"]] = relationship(
        "Segment", back_populates="meeting", cascade="all, delete-orphan"
    )
    insights: Mapped[List["Insight"]] = relationship(
        "Insight", back_populates="meeting", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Meeting(id={self.id}, title='{self.title}', status={self.status})>"