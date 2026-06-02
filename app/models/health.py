import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SensorReadingMixin(UUIDPrimaryKeyMixin, TimestampMixin):
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_payload: Mapped[dict | None] = mapped_column(JSONB)


class HeartRateReading(Base, SensorReadingMixin):
    __tablename__ = "heart_rate_readings"
    __table_args__ = (UniqueConstraint("device_id", "recorded_at", name="uq_hr_device_time"),)

    bpm: Mapped[int] = mapped_column(Integer)


class HrvReading(Base, SensorReadingMixin):
    __tablename__ = "hrv_readings"
    __table_args__ = (UniqueConstraint("device_id", "recorded_at", name="uq_hrv_device_time"),)

    rmssd_ms: Mapped[float] = mapped_column(Float)


class Spo2Reading(Base, SensorReadingMixin):
    __tablename__ = "spo2_readings"
    __table_args__ = (UniqueConstraint("device_id", "recorded_at", name="uq_spo2_device_time"),)

    percentage: Mapped[float] = mapped_column(Float)


class ActivityReading(Base, SensorReadingMixin):
    __tablename__ = "activity_readings"
    __table_args__ = (UniqueConstraint("device_id", "recorded_at", name="uq_activity_device_time"),)

    steps: Mapped[int | None] = mapped_column(Integer)
    calories_kcal: Mapped[float | None] = mapped_column(Float)
    distance_meters: Mapped[float | None] = mapped_column(Float)
    active_minutes: Mapped[int | None] = mapped_column(Integer)


class SleepSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sleep_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    score: Mapped[int | None] = mapped_column(Integer)
    stages: Mapped[dict | None] = mapped_column(JSONB)
    source_payload: Mapped[dict | None] = mapped_column(JSONB)


class StressReading(Base, SensorReadingMixin):
    __tablename__ = "stress_readings"
    __table_args__ = (UniqueConstraint("device_id", "recorded_at", name="uq_stress_device_time"),)

    score: Mapped[int] = mapped_column(Integer)


class SkinTemperatureReading(Base, SensorReadingMixin):
    __tablename__ = "skin_temperature_readings"
    __table_args__ = (UniqueConstraint("device_id", "recorded_at", name="uq_temp_device_time"),)

    celsius: Mapped[float] = mapped_column(Float)


class Workout(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workouts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    workout_type: Mapped[str] = mapped_column(String(128), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    calories_kcal: Mapped[float | None] = mapped_column(Float)
    avg_heart_rate: Mapped[int | None] = mapped_column(Integer)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    source_payload: Mapped[dict | None] = mapped_column(JSONB)

