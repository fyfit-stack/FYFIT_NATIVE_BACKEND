from typing import Annotated
from uuid import UUID
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.user_service import UserService
from pydantic import ValidationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except (jwt.PyJWTError, ValidationError):
        raise credentials_exception

    user = await UserService(db).get_by_id(UUID(user_id_str))
    if user is None:
        raise credentials_exception
    return user

