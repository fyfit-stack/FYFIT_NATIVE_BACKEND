from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.device import DeviceActivePatch, DevicePairRequest, DeviceSchema
from app.services.device_service import DeviceService

router = APIRouter()


@router.post("/pair", response_model=DeviceSchema, status_code=status.HTTP_201_CREATED)
async def pair_device(
    payload: DevicePairRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await DeviceService(db).pair(current_user, payload)


@router.get("", response_model=list[DeviceSchema])
async def list_devices(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await DeviceService(db).list_for_user(current_user)


@router.patch("/{device_id}/active", response_model=DeviceSchema)
async def set_active(
    device_id: UUID,
    payload: DeviceActivePatch,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await DeviceService(db).set_active(current_user, device_id, payload.is_active)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await DeviceService(db).delete(current_user, device_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

