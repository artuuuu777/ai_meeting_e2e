from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.meeting import Meeting
from app.models.enums import MeetingStatus, ProcessingStatus
from app.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    PresignedUploadResponse,
)
from app.services.s3 import S3Service
from app.workers.tasks import process_audio_file

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=MeetingResponse)
async def create_meeting(
    meeting_in: MeetingCreate,
    db: AsyncSession = Depends(get_db),
) -> Meeting:
    """Create a new meeting."""
    meeting = Meeting(**meeting_in.model_dump())
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    logger.info("Meeting created", meeting_id=str(meeting.id))
    return meeting


@router.get("/", response_model=MeetingListResponse)
async def list_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[MeetingStatus] = None,
    processing_status: Optional[ProcessingStatus] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List meetings with pagination."""
    query = select(Meeting).where(Meeting.is_deleted == False)
    
    if status:
        query = query.where(Meeting.status == status)
    if processing_status:
        query = query.where(Meeting.processing_status == processing_status)
    
    # Get total count
    count_query = select(Meeting).where(Meeting.is_deleted == False)
    if status:
        count_query = count_query.where(Meeting.status == status)
    if processing_status:
        count_query = count_query.where(Meeting.processing_status == processing_status)
    
    total = len((await db.execute(count_query)).all())
    
    # Get paginated results
    query = query.order_by(Meeting.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    meetings = result.scalars().all()
    
    return {
        "items": meetings,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Meeting:
    """Get a specific meeting by ID."""
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.is_deleted == False)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meeting


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: UUID,
    meeting_update: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
) -> Meeting:
    """Update a meeting."""
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.is_deleted == False)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    update_data = meeting_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meeting, field, value)
    
    await db.commit()
    await db.refresh(meeting)
    
    logger.info("Meeting updated", meeting_id=str(meeting_id))
    return meeting


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Soft delete a meeting."""
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.is_deleted == False)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    meeting.is_deleted = True
    await db.commit()
    
    logger.info("Meeting deleted", meeting_id=str(meeting_id))
    return {"message": "Meeting deleted successfully"}


@router.post("/{meeting_id}/upload-url", response_model=PresignedUploadResponse)
async def get_upload_url(
    meeting_id: UUID,
    filename: str = Query(..., description="Original filename"),
    content_type: str = Query("audio/wav", description="MIME type"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a presigned URL for uploading audio file."""
    # Verify meeting exists
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.is_deleted == False)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Generate S3 key
    file_extension = filename.split(".")[-1].lower()
    if file_extension not in settings.SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {settings.SUPPORTED_AUDIO_FORMATS}",
        )
    
    s3_key = f"uploads/{meeting_id}/{datetime.utcnow().isoformat()}.{file_extension}"
    
    # Generate presigned URL
    s3_service = S3Service()
    try:
        presigned_url = s3_service.generate_presigned_upload_url(
            bucket=settings.S3_BUCKET_RAW_AUDIO,
            key=s3_key,
            content_type=content_type,
            expires_in=900,  # 15 minutes
        )
    except ClientError as e:
        logger.error("Failed to generate presigned URL", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")
    
    # Update meeting with S3 URI
    meeting.s3_audio_uri = f"s3://{settings.S3_BUCKET_RAW_AUDIO}/{s3_key}"
    meeting.processing_status = ProcessingStatus.PENDING
    await db.commit()
    
    # Trigger async processing
    process_audio_file.delay(str(meeting_id), s3_key)
    
    logger.info(
        "Presigned URL generated",
        meeting_id=str(meeting_id),
        s3_key=s3_key,
    )
    
    return {
        "upload_url": presigned_url,
        "s3_key": s3_key,
        "expires_at": datetime.utcnow() + timedelta(minutes=15),
    }


@router.post("/{meeting_id}/upload-direct")
async def upload_audio_direct(
    meeting_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Direct upload of audio file (for smaller files)."""
    # Verify meeting exists
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.is_deleted == False)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Read file content and validate size
    file_content = await file.read()
    if len(file_content) > settings.max_audio_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_AUDIO_FILE_SIZE_MB}MB",
        )
    
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {settings.SUPPORTED_AUDIO_FORMATS}",
        )
    
    # Upload to S3
    s3_key = f"uploads/{meeting_id}/{datetime.utcnow().isoformat()}.{file_extension}"
    s3_service = S3Service()
    
    try:
        s3_service.upload_file(
            bucket=settings.S3_BUCKET_RAW_AUDIO,
            key=s3_key,
            file_content=file_content,
            content_type=file.content_type,
        )
    except Exception as e:
        logger.error("Failed to upload file to S3", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload file")
    
    # Update meeting
    meeting.s3_audio_uri = f"s3://{settings.S3_BUCKET_RAW_AUDIO}/{s3_key}"
    meeting.processing_status = ProcessingStatus.PENDING
    await db.commit()
    
    # Trigger async processing
    process_audio_file.delay(str(meeting_id), s3_key)
    
    logger.info(
        "Audio file uploaded directly",
        meeting_id=str(meeting_id),
        s3_key=s3_key,
        file_size=len(file_content),
    )
    
    return {
        "message": "File uploaded successfully",
        "s3_key": s3_key,
        "processing_status": "started",
    }