from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.meeting import Meeting
from app.schemas.questions import QuestionRequest, QuestionResponse
from app.services.rag import RAGService

router = APIRouter()


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Ask a question about meeting content using RAG."""
    
    # Verify meeting exists if meeting_id provided
    if request.meeting_id:
        result = await db.execute(
            select(Meeting).where(
                Meeting.id == request.meeting_id,
                Meeting.is_deleted == False,
            )
        )
        meeting = result.scalar_one_or_none()
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Perform RAG
    rag_service = RAGService(db)
    response = await rag_service.answer_question(
        question=request.question,
        meeting_id=request.meeting_id,
        max_context_segments=request.max_context_segments,
        include_sources=request.include_sources,
    )
    
    return response