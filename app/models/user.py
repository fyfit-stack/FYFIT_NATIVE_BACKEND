import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, SmallInteger, DateTime
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    firebase_uid: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(60))
    last_name: Mapped[str | None] = mapped_column(String(60))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    gender: Mapped[str | None] = mapped_column(String(10))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    profile_pic_url: Mapped[str | None] = mapped_column(String(1024))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    health_profile: Mapped["UserHealthProfile | None"] = relationship(back_populates="user")
    devices = relationship("Device", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")


class UserSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    device_name: Mapped[str | None] = mapped_column(String(100))
    device_type: Mapped[str | None] = mapped_column(String(20))
    ip_address: Mapped[str | None] = mapped_column(INET)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    user: Mapped[User] = relationship(back_populates="sessions")


class UserHealthProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_health_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    bmi: Mapped[float | None] = mapped_column(
        Float,
        sa.Computed("weight_kg / ((height_cm/100) * (height_cm/100))", persisted=True)
    )
    body_fat_pct: Mapped[float | None] = mapped_column(Float)
    fitness_goal: Mapped[str | None] = mapped_column(String(30))
    activity_level: Mapped[str | None] = mapped_column(String(20))
    daily_step_goal: Mapped[int | None] = mapped_column(Integer, default=8000)
    daily_calorie_goal: Mapped[int | None] = mapped_column(Integer, default=2000)
    daily_water_goal_ml: Mapped[int | None] = mapped_column(Integer, default=2500)
    sleep_goal_hours: Mapped[float | None] = mapped_column(Float, default=8.0)
    target_weight_kg: Mapped[float | None] = mapped_column(Float)
    target_date: Mapped[date | None] = mapped_column(Date)
    resting_hr_baseline: Mapped[int | None] = mapped_column(SmallInteger)
    hrv_baseline: Mapped[float | None] = mapped_column(Float)

    user: Mapped[User] = relationship(back_populates="health_profile")
