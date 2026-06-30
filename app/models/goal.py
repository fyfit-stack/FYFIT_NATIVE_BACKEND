import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, SmallInteger, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class UserGoalProgress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_goals_progress"
    __table_args__ = (UniqueConstraint("user_id", "recorded_date", name="idx_goals_user_date"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recorded_date: Mapped[date] = mapped_column(Date, index=True)
    steps_achieved: Mapped[int | None] = mapped_column(Integer, default=0)
    steps_goal: Mapped[int] = mapped_column(Integer)
    calories_burned: Mapped[float | None] = mapped_column(Float, default=0)
    calories_goal: Mapped[int] = mapped_column(Integer)
    active_minutes: Mapped[int | None] = mapped_column(Integer, default=0)
    sleep_hours: Mapped[float | None] = mapped_column(Float, default=0)
    sleep_goal_hours: Mapped[float] = mapped_column(Float)
    water_ml: Mapped[int | None] = mapped_column(Integer, default=0)
    water_goal_ml: Mapped[int] = mapped_column(Integer)
    day_score: Mapped[int | None] = mapped_column(SmallInteger, default=0)
    goal_met: Mapped[bool] = mapped_column(Boolean, default=False)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

