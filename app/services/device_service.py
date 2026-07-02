from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.user import User
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DevicePairRequest


class DeviceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.devices = DeviceRepository(db)

    async def pair(self, user: User, payload: DevicePairRequest) -> Device:
        existing = await self.devices.get_by_user_serial(user.id, payload.serial_number)
        if existing is not None:
            return existing

        device = Device(
            user_id=user.id,
            category=payload.device_type,
            model_name=payload.model,
            serial_number=payload.serial_number,
            firmware_version=payload.firmware_version,
            display_name=payload.display_name or f"{payload.model} Device",
            metadata_=payload.metadata,
            paired_at=datetime.now(timezone.utc),
        )
        await self.devices.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def list_for_user(self, user: User) -> list[Device]:
        return await self.devices.list_for_user(user.id)

    async def require_owned(self, user: User, device_id: UUID) -> Device:
        device = await self.devices.get_owned(user.id, device_id)
        if device is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        return device

    async def set_active(self, user: User, device_id: UUID, is_active: bool) -> Device:
        device = await self.require_owned(user, device_id)
        device.is_active = is_active
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def delete(self, user: User, device_id: UUID) -> None:
        device = await self.require_owned(user, device_id)
        device.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def mark_synced(self, device: Device) -> None:
        device.last_sync_at = datetime.now(timezone.utc)
