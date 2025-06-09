from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.meeting import Meeting
from app.models.enums import TemplateType, ProcessingStatus
from app.models.insight import Insight, TemplateRun
from app.schemas.template import TemplateRunRequest, TemplateRunResponse, InsightResponse
from app.workers.tasks import run_template_analysis

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_templates() -> List[dict]:
    """List all available analysis templates."""
    templates = [
        {
            "id": template.value,
            "name": template.value.replace("_", " ").title(),
            "description": get_template_description(template),
        }
        for template in TemplateType
    ]
    return templates


@router.post("/{template_id}/run", response_model=TemplateRunResponse)
async def run_template(
    template_id: str,
    request: TemplateRunRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Run a specific template analysis on a meeting."""
    
    # Validate template
    try:
        template_type = TemplateType(template_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid template ID")
    
    # Verify meeting exists and is processed
    result = await db.execute(
        select(Meeting).where(
            Meeting.id == request.meeting_id,
            Meeting.is_deleted == False,
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.processing_status != ProcessingStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Meeting must be fully processed before running templates",
        )
    
    # Trigger async template analysis
    task = run_template_analysis.delay(
        str(request.meeting_id),
        template_type.value,
        request.parameters or {},
    )
    
    return {
        "task_id": task.id,
        "status": "started",
        "template_id": template_id,
        "meeting_id": request.meeting_id,
    }


@router.get("/{template_id}/results/{meeting_id}", response_model=List[InsightResponse])
async def get_template_results(
    template_id: str,
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[Insight]:
    """Get template analysis results for a meeting."""
    
    # Validate template
    try:
        template_type = TemplateType(template_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid template ID")
    
    # Get insights
    result = await db.execute(
        select(Insight).where(
            Insight.meeting_id == meeting_id,
            Insight.insight_type == template_type,
        )
    )
    insights = result.scalars().all()
    
    return insights


def get_template_description(template_type: TemplateType) -> str:
    """Get description for a template type."""
    descriptions = {
        TemplateType.KEY_POINTS: "Extract key discussion points and takeaways",
        TemplateType.ACTION_ITEMS: "Identify action items with owners and due dates",
        TemplateType.DECISIONS: "Capture decisions made during the meeting",
        TemplateType.RISKS: "Identify risks and potential mitigation strategies",
        TemplateType.BLOCKERS: "Find blockers and impediments discussed",
        TemplateType.FOLLOW_UPS: "List follow-up items and next steps",
        TemplateType.PARKING_LOT: "Capture topics deferred for future discussion",
        TemplateType.ROADMAP: "Extract roadmap and timeline discussions",
        TemplateType.KUDOS: "Identify recognition and positive feedback",
    }
    return descriptions.get(template_type, "Analysis template")