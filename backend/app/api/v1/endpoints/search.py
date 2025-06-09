from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.segment import Segment
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.embeddings import EmbeddingService

router = APIRouter()
embedding_service = EmbeddingService()


@router.get("/", response_model=SearchResponse)
async def semantic_search(
    q: str = Query(..., description="Search query"),
    meeting_id: Optional[UUID] = Query(None, description="Filter by meeting ID"),
    limit: int = Query(10, ge=1, le=50),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Similarity threshold"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Perform semantic search across meeting transcripts."""
    
    # Generate embedding for query
    query_embedding = await embedding_service.generate_embedding(q)
    
    # Build the vector search query
    search_query = f"""
    SELECT 
        s.id,
        s.meeting_id,
        s.text,
        s.speaker,
        s.start_time_seconds,
        s.end_time_seconds,
        1 - (s.embedding <=> :embedding::vector) as similarity,
        m.title as meeting_title,
        m.scheduled_at as meeting_date
    FROM segments s
    JOIN meetings m ON s.meeting_id = m.id
    WHERE 
        s.embedding IS NOT NULL
        AND m.is_deleted = false
        {f"AND s.meeting_id = :meeting_id" if meeting_id else ""}
        AND 1 - (s.embedding <=> :embedding::vector) > :threshold
    ORDER BY similarity DESC
    LIMIT :limit
    """
    
    # Execute search
    params = {
        "embedding": str(query_embedding),
        "threshold": threshold,
        "limit": limit,
    }
    if meeting_id:
        params["meeting_id"] = meeting_id
    
    result = await db.execute(text(search_query), params)
    rows = result.fetchall()
    
    # Format results
    results = []
    for row in rows:
        results.append(
            SearchResult(
                segment_id=row.id,
                meeting_id=row.meeting_id,
                meeting_title=row.meeting_title,
                meeting_date=row.meeting_date,
                text=row.text,
                speaker=row.speaker,
                start_time=row.start_time_seconds,
                end_time=row.end_time_seconds,
                similarity_score=row.similarity,
            )
        )
    
    return SearchResponse(
        query=q,
        results=results,
        total=len(results),
    )


@router.post("/batch", response_model=List[SearchResponse])
async def batch_search(
    requests: List[SearchRequest],
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Perform multiple semantic searches in batch."""
    responses = []
    
    for request in requests:
        response = await semantic_search(
            q=request.query,
            meeting_id=request.meeting_id,
            limit=request.limit,
            threshold=request.threshold,
            db=db,
        )
        responses.append(response)
    
    return responses