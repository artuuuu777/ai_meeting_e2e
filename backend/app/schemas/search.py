from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    meeting_id: Optional[UUID] = None
    limit: int = Field(default=10, ge=1, le=50)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    segment_id: UUID
    meeting_id: UUID
    meeting_title: str
    meeting_date: Optional[datetime]
    text: str
    speaker: Optional[str]
    start_time: float
    end_time: float
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int