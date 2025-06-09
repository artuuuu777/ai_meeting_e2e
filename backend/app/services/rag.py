from typing import List, Optional
from uuid import UUID

import google.generativeai as genai
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.questions import QuestionResponse, Source
from app.services.embeddings import EmbeddingService

logger = get_logger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def answer_question(
        self,
        question: str,
        meeting_id: Optional[UUID] = None,
        max_context_segments: int = 8,
        include_sources: bool = True,
    ) -> QuestionResponse:
        """Answer a question using RAG."""
        
        # Get relevant segments
        segments = await self._get_relevant_segments(
            question, meeting_id, max_context_segments
        )
        
        if not segments:
            return QuestionResponse(
                question=question,
                answer="I couldn't find any relevant information to answer your question.",
                sources=[],
                confidence_score=0.0,
                tokens_used=0,
            )
        
        # Build context
        context = self._build_context(segments)
        
        # Generate answer
        prompt = f"""Based on the following meeting transcript excerpts, answer the question.
Be specific and cite the relevant parts when possible.

Context:
{context}

Question: {question}

Answer:"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Calculate confidence (simplified)
            avg_similarity = sum(s["similarity"] for s in segments) / len(segments)
            confidence_score = min(avg_similarity * 1.2, 1.0)  # Scale up slightly
            
            # Prepare sources
            sources = []
            if include_sources:
                for segment in segments[:5]:  # Top 5 sources
                    sources.append(
                        Source(
                            segment_id=segment["id"],
                            meeting_id=segment["meeting_id"],
                            meeting_title=segment["meeting_title"],
                            text=segment["text"],
                            speaker=segment["speaker"],
                            timestamp=segment["start_time_seconds"],
                            relevance_score=segment["similarity"],
                        )
                    )
            
            return QuestionResponse(
                question=question,
                answer=answer,
                sources=sources,
                confidence_score=confidence_score,
                tokens_used=response.usage_metadata.total_token_count,
            )
            
        except Exception as e:
            logger.error("Failed to generate answer", error=str(e))
            raise

    async def _get_relevant_segments(
        self,
        query: str,
        meeting_id: Optional[UUID],
        limit: int,
    ) -> List[dict]:
        """Get relevant segments using vector search."""
        
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Build search query
        search_query = f"""
        SELECT 
            s.id,
            s.meeting_id,
            s.text,
            s.speaker,
            s.start_time_seconds,
            s.end_time_seconds,
            1 - (s.embedding <=> :embedding::vector) as similarity,
            m.title as meeting_title
        FROM segments s
        JOIN meetings m ON s.meeting_id = m.id
        WHERE 
            s.embedding IS NOT NULL
            AND m.is_deleted = false
            {f"AND s.meeting_id = :meeting_id" if meeting_id else ""}
            AND 1 - (s.embedding <=> :embedding::vector) > 0.5
        ORDER BY similarity DESC
        LIMIT :limit
        """
        
        params = {
            "embedding": str(query_embedding),
            "limit": limit,
        }
        if meeting_id:
            params["meeting_id"] = meeting_id
        
        result = await self.db.execute(text(search_query), params)
        rows = result.fetchall()
        
        segments = []
        for row in rows:
            segments.append({
                "id": row.id,
                "meeting_id": row.meeting_id,
                "meeting_title": row.meeting_title,
                "text": row.text,
                "speaker": row.speaker,
                "start_time_seconds": row.start_time_seconds,
                "end_time_seconds": row.end_time_seconds,
                "similarity": row.similarity,
            })
        
        return segments

    def _build_context(self, segments: List[dict]) -> str:
        """Build context string from segments."""
        context_parts = []
        
        for i, segment in enumerate(segments):
            speaker = segment["speaker"] or "Unknown"
            time = self._format_time(segment["start_time_seconds"])
            text = segment["text"]
            
            context_parts.append(
                f"[{i+1}] {speaker} at {time}: {text}"
            )
        
        return "\n\n".join(context_parts)

    def _format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"