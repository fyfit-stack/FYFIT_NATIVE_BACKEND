from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.firebase import verify_firebase_token
from app.models.user import User
from app.services.user_service import UserService


async def get_current_user(
    token: Annotated[dict, Depends(verify_firebase_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    return await UserService(db).get_or_create_from_firebase(token)

