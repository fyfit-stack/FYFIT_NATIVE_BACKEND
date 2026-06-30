import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, BigIntPrimaryKeyMixin


class TimescaleReadingMixin(BigIntPrimaryKeyMixin):
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"), index=True, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class HeartRateReading(Base, TimescaleReadingMixin):
    __tablename__ = "heart_rate_readings"
    
    bpm: Mapped[int] = mapped_column(SmallInteger)
    reading_type: Mapped[str] = mapped_column(String(15))
    quality_score: Mapped[int | None] = mapped_column(SmallInteger)


class HrvReading(Base, TimescaleReadingMixin):
    __tablename__ = "hrv_readings"

    rmssd_ms: Mapped[float] = mapped_column(Float)
    sdnn_ms: Mapped[float | None] = mapped_column(Float)
    lf_power: Mapped[float | None] = mapped_column(Float)
    hf_power: Mapped[float | None] = mapped_column(Float)
    reading_type: Mapped[str] = mapped_column(String(15))


class Spo2Reading(Base, TimescaleReadingMixin):
    __tablename__ = "spo2_readings"

    spo2_pct: Mapped[float] = mapped_column(Float)
    reading_type: Mapped[str] = mapped_column(String(15))
    quality_score: Mapped[int | None] = mapped_column(SmallInteger)


class StressReading(Base, TimescaleReadingMixin):
    __tablename__ = "stress_readings"

    stress_score: Mapped[int] = mapped_column(SmallInteger)
    stress_label: Mapped[str | None] = mapped_column(String(15))


class SkinTemperatureReading(Base, TimescaleReadingMixin):
    __tablename__ = "skin_temperature_readings"

    temperature_c: Mapped[float] = mapped_column(Float)
    baseline_c: Mapped[float | None] = mapped_column(Float)
    deviation_c: Mapped[float | None] = mapped_column(Float)


class ActivityReading(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "activity_readings"
    __table_args__ = (UniqueConstraint("user_id", "device_id", "recorded_date", name="idx_activity_user_device_date"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    recorded_date: Mapped[date] = mapped_column(Date, index=True)
    steps: Mapped[int | None] = mapped_column(Integer, default=0)
    distance_km: Mapped[float | None] = mapped_column(Float, default=0)
    calories_burned: Mapped[float | None] = mapped_column(Float, default=0)
    active_minutes: Mapped[int | None] = mapped_column(Integer, default=0)
    sedentary_min: Mapped[int | None] = mapped_column(Integer, default=0)
    floors_climbed: Mapped[int | None] = mapped_column(Integer, default=0)
    elevation_m: Mapped[float | None] = mapped_column(Float, default=0)
    hourly_steps: Mapped[dict | None] = mapped_column(JSONB)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SleepSession(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "sleep_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    sleep_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sleep_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_sleep_min: Mapped[int] = mapped_column(Integer)
    deep_sleep_min: Mapped[int | None] = mapped_column(Integer, default=0)
    rem_sleep_min: Mapped[int | None] = mapped_column(Integer, default=0)
    light_sleep_min: Mapped[int | None] = mapped_column(Integer, default=0)
    awake_min: Mapped[int | None] = mapped_column(Integer, default=0)
    sleep_efficiency_pct: Mapped[float | None] = mapped_column(Float)
    sleep_score: Mapped[int | None] = mapped_column(SmallInteger)
    avg_hr: Mapped[float | None] = mapped_column(Float)
    avg_spo2_pct: Mapped[float | None] = mapped_column(Float)
    avg_hrv_ms: Mapped[float | None] = mapped_column(Float)
    lowest_hr: Mapped[int | None] = mapped_column(SmallInteger)
    snore_minutes: Mapped[int | None] = mapped_column(Integer, default=0)
    recorded_date: Mapped[date] = mapped_column(Date)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Workout(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "workouts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    workout_type: Mapped[str] = mapped_column(String(30), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_min: Mapped[int] = mapped_column(Integer)
    calories: Mapped[float | None] = mapped_column(Float, default=0)
    avg_hr: Mapped[float | None] = mapped_column(Float)
    max_hr: Mapped[float | None] = mapped_column(Float)
    min_hr: Mapped[float | None] = mapped_column(Float)
    steps: Mapped[int | None] = mapped_column(Integer, default=0)
    distance_km: Mapped[float | None] = mapped_column(Float, default=0)
    avg_pace: Mapped[float | None] = mapped_column(Float)
    elevation_m: Mapped[float | None] = mapped_column(Float, default=0)
    avg_spo2_pct: Mapped[float | None] = mapped_column(Float)
    avg_stress: Mapped[int | None] = mapped_column(SmallInteger)
    workout_score: Mapped[int | None] = mapped_column(SmallInteger)
    notes: Mapped[str | None] = mapped_column(String)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

