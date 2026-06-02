from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.sync import BatchSyncRequest, BatchSyncResult
from app.services.sync_service import SyncService

router = APIRouter()


@router.post("/batch", response_model=BatchSyncResult)
async def batch_sync(
    payload: BatchSyncRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await SyncService(db).sync_batch(current_user, payload)

