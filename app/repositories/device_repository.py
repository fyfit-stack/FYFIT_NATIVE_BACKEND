from uuid import UUID

from sqlalchemy import select

from app.models.device import Device
from app.repositories.base import BaseRepository


class DeviceRepository(BaseRepository[Device]):
    model = Device

    async def list_for_user(self, user_id: UUID) -> list[Device]:
        result = await self.db.execute(
            select(Device).where(Device.user_id == user_id, Device.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    async def get_by_user_serial(self, user_id: UUID, serial_number: str) -> Device | None:
        return await self.first(
            select(Device).where(
                Device.user_id == user_id,
                Device.serial_number == serial_number,
                Device.deleted_at.is_(None),
            )
        )

    async def get_owned(self, user_id: UUID, device_id: UUID) -> Device | None:
        return await self.first(
            select(Device).where(
                Device.id == device_id,
                Device.user_id == user_id,
                Device.deleted_at.is_(None),
            )
        )

