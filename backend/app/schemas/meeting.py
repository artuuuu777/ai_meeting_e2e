from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import MeetingStatus, ProcessingStatus


class MeetingBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    participants: List[str] = Field(default_factory=list)
    organizer_id: Optional[UUID] = None


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    participants: Optional[List[str]] = None
    status: Optional[MeetingStatus] = None


class MeetingResponse(MeetingBase):
    id: UUID
    status: MeetingStatus
    processing_status: ProcessingStatus
    duration_seconds: Optional[int] = None
    s3_audio_uri: Optional[str] = None
    s3_transcript_uri: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_cost_usd: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    items: List[MeetingResponse]
    total: int
    skip: int
    limit: int


class PresignedUploadResponse(BaseModel):
    upload_url: str
    s3_key: str
    expires_at: datetime