from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import JSON, Enum, ForeignKey, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import TemplateType

if TYPE_CHECKING:
    from app.models.meeting import Meeting


class TemplateRun(Base, TimestampMixin):
    __tablename__ = "template_runs"
    
    # Foreign key
    meeting_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False
    )
    
    # Template info
    template_type: Mapped[TemplateType] = mapped_column(
        Enum(TemplateType), nullable=False
    )
    template_version: Mapped[str] = mapped_column(String(20), default="1.0")
    
    # Prompt details
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Results
    raw_response: Mapped[str] = mapped_column(Text, nullable=False)
    structured_output: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Metrics
    prompt_tokens: Mapped[Optional[int]] = mapped_column()
    completion_tokens: Mapped[Optional[int]] = mapped_column()
    total_tokens: Mapped[Optional[int]] = mapped_column()
    cost_usd: Mapped[Optional[float]] = mapped_column(Float)
    latency_ms: Mapped[Optional[int]] = mapped_column()
    
    # Model info
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_parameters: Mapped[dict] = mapped_column(JSON, default=dict)


class Insight(Base, TimestampMixin):
    __tablename__ = "insights"
    
    # Foreign keys
    meeting_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False
    )
    template_run_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("template_runs.id")
    )
    
    # Insight details
    insight_type: Mapped[TemplateType] = mapped_column(
        Enum(TemplateType), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Structured data (varies by type)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Priority/importance
    priority: Mapped[Optional[str]] = mapped_column(String(20))
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="insights")
    
    def __repr__(self) -> str:
        return f"<Insight(id={self.id}, type={self.insight_type}, title='{self.title}')>"