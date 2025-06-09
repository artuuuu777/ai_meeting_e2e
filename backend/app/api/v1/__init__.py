from fastapi import APIRouter

from app.api.v1.endpoints import meetings, search, questions, templates, webhooks, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])