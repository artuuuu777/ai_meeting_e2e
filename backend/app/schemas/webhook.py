from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class TranscriptionCompleteWebhook(BaseModel):
    meeting_id: UUID
    transcript_s3_uri: str
    duration_seconds: int
    word_count: int
    confidence_score: float
    completed_at: datetime = datetime.utcnow()


class AnalysisCompleteWebhook(BaseModel):
    meeting_id: UUID
    templates_completed: List[str]
    total_insights: int
    total_cost_usd: float
    completed_at: datetime = datetime.utcnow()