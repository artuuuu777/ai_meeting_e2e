from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.meeting import Meeting
from app.models.enums import ProcessingStatus
from app.schemas.webhook import TranscriptionCompleteWebhook, AnalysisCompleteWebhook

router = APIRouter()
logger = get_logger(__name__)


@router.post("/transcript")
async def transcription_complete(
    webhook: TranscriptionCompleteWebhook,
    x_webhook_token: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Handle transcription completion webhook from Step Functions."""
    
    # Verify webhook token (in production, use proper authentication)
    # if x_webhook_token != settings.WEBHOOK_SECRET:
    #     raise HTTPException(status_code=401, detail="Invalid webhook token")
    
    # Update meeting status
    result = await db.execute(
        select(Meeting).where(Meeting.id == webhook.meeting_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        logger.error("Meeting not found for webhook", meeting_id=str(webhook.meeting_id))
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Update processing status and transcript location
    meeting.processing_status = ProcessingStatus.EMBEDDING
    meeting.s3_transcript_uri = webhook.transcript_s3_uri
    meeting.duration_seconds = webhook.duration_seconds
    meeting.metadata.update({
        "transcription_confidence": webhook.confidence_score,
        "word_count": webhook.word_count,
    })
    
    await db.commit()
    
    logger.info(
        "Transcription completed",
        meeting_id=str(webhook.meeting_id),
        duration=webhook.duration_seconds,
    )
    
    return {"status": "accepted", "meeting_id": str(webhook.meeting_id)}


@router.post("/analysis")
async def analysis_complete(
    webhook: AnalysisCompleteWebhook,
    x_webhook_token: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Handle analysis completion webhook."""
    
    # Update meeting status
    result = await db.execute(
        select(Meeting).where(Meeting.id == webhook.meeting_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        logger.error("Meeting not found for webhook", meeting_id=str(webhook.meeting_id))
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Update processing status and costs
    meeting.processing_status = ProcessingStatus.COMPLETED
    meeting.processing_completed_at = webhook.completed_at
    meeting.processing_cost_usd = webhook.total_cost_usd
    meeting.metadata.update({
        "templates_completed": webhook.templates_completed,
        "total_insights": webhook.total_insights,
    })
    
    await db.commit()
    
    logger.info(
        "Analysis completed",
        meeting_id=str(webhook.meeting_id),
        templates=webhook.templates_completed,
        cost=webhook.total_cost_usd,
    )
    
    return {"status": "accepted", "meeting_id": str(webhook.meeting_id)}