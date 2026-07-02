import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, SmallInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Device(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "devices"
    # Keeping the old unique constraint if serial_number is not globally unique in current data, but spec says "globally unique". Let's stick to unique on serial_number column.
    # The spec specifies serial_number UNIQUE. So we can add unique=True.

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    display_name: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(20))
    model_name: Mapped[str | None] = mapped_column(String(80))
    manufacturer: Mapped[str | None] = mapped_column(String(60))
    serial_number: Mapped[str | None] = mapped_column(String(60), unique=True)
    bluetooth_mac: Mapped[str | None] = mapped_column(String(20))
    firmware_version: Mapped[str | None] = mapped_column(String(30))
    battery_level: Mapped[int | None] = mapped_column(SmallInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_paired: Mapped[bool] = mapped_column(Boolean, default=True)
    paired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)

    user = relationship("User", back_populates="devices")

    @property
    def device_type(self) -> str:
        return self.category

    @property
    def model(self) -> str | None:
        return self.model_name

