from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    meeting_id: Optional[UUID] = None
    max_context_segments: int = Field(default=8, ge=1, le=20)
    include_sources: bool = Field(default=True)


class Source(BaseModel):
    segment_id: UUID
    meeting_id: UUID
    meeting_title: str
    text: str
    speaker: Optional[str]
    timestamp: float
    relevance_score: float


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: Optional[List[Source]] = None
    confidence_score: float
    tokens_used: int