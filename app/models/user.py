import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(320), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))
    photo_url: Mapped[str | None] = mapped_column(String(1024))

    health_profile: Mapped["UserHealthProfile | None"] = relationship(back_populates="user")
    devices = relationship("Device", back_populates="user")


class UserHealthProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_health_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    gender: Mapped[str | None] = mapped_column(String(32))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    bmi: Mapped[float | None] = mapped_column(Float)
    activity_level: Mapped[str | None] = mapped_column(String(64))
    fitness_goal: Mapped[str | None] = mapped_column(String(128))
    daily_step_goal: Mapped[int | None] = mapped_column(Integer)
    water_goal_ml: Mapped[int | None] = mapped_column(Integer)
    sleep_goal_minutes: Mapped[int | None] = mapped_column(Integer)
    target_weight_kg: Mapped[float | None] = mapped_column(Float)
    baseline_hr: Mapped[int | None] = mapped_column(Integer)
    baseline_hrv: Mapped[float | None] = mapped_column(Float)

    user: Mapped[User] = relationship(back_populates="health_profile")
