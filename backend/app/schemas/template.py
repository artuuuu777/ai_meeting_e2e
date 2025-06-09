from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import TemplateType


class TemplateRunRequest(BaseModel):
    meeting_id: UUID
    parameters: Optional[Dict[str, Any]] = None


class TemplateRunResponse(BaseModel):
    task_id: str
    status: str
    template_id: str
    meeting_id: UUID


class InsightResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    insight_type: TemplateType
    title: str
    content: str
    data: Dict[str, Any]
    priority: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True