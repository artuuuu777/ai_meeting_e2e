from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.meeting import Meeting


class Segment(Base, TimestampMixin):
    __tablename__ = "segments"

    # Foreign key
    meeting_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False
    )
    
    # Segment info
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    end_time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    speaker: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Embedding
    embedding: Mapped[Optional[Vector]] = mapped_column(Vector(1536))
    
    # Confidence scores
    transcription_confidence: Mapped[Optional[float]] = mapped_column(Float)
    speaker_confidence: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="segments")
    
    def __repr__(self) -> str:
        return f"<Segment(id={self.id}, meeting_id={self.meeting_id}, seq={self.sequence_number})>"