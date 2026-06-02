from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserHealthProfileSchema, UserProfileUpsert
from app.services.user_service import UserService

router = APIRouter()


@router.patch("/profile", response_model=UserHealthProfileSchema)
async def upsert_profile(
    payload: UserProfileUpsert,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await UserService(db).upsert_profile(current_user, payload)

