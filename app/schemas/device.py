from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema


class DevicePairRequest(BaseModel):
    device_type: str = Field(examples=["ring", "band", "watch"])
    model: str = Field(examples=["SYO1", "SR16", "Y65", "WATCH"])
    serial_number: str
    firmware_version: str | None = None
    display_name: str | None = None
    metadata: dict | None = None


class DeviceSchema(TimestampedSchema):
    user_id: UUID
    device_type: str
    model: str
    serial_number: str
    firmware_version: str | None = None
    display_name: str | None = None
    is_active: bool
    last_sync_at: datetime | None = None
    metadata_: dict | None = None


class DeviceActivePatch(BaseModel):
    is_active: bool

