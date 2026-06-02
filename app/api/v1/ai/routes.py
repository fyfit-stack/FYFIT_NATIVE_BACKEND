from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.ai import AISuggestionRequest, AISuggestionSchema
from app.services.ai_service import AIInsightService

router = APIRouter()


@router.post("/suggestions", response_model=AISuggestionSchema)
async def generate_suggestion(
    payload: AISuggestionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await AIInsightService(db).generate(current_user, payload.suggestion_type)

