from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import (
    ActivityReading,
    HeartRateReading,
    HrvReading,
    SkinTemperatureReading,
    SleepSession,
    Spo2Reading,
    StressReading,
)


class HealthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def bulk_add(self, rows: list[object]) -> int:
        if not rows:
            return 0
        self.db.add_all(rows)
        await self.db.flush()
        return len(rows)

    async def readings(
        self,
        model: type,
        user_id: UUID,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list:
        statement: Select = select(model).where(model.user_id == user_id)
        if start:
            statement = statement.where(model.recorded_at >= start)
        if end:
            statement = statement.where(model.recorded_at <= end)
        result = await self.db.execute(
            statement.order_by(desc(model.recorded_at)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def summary(self, user_id: UUID) -> dict:
        latest_hr = await self.db.execute(
            select(HeartRateReading).where(HeartRateReading.user_id == user_id).order_by(
                desc(HeartRateReading.recorded_at)
            ).limit(1)
        )
        latest_spo2 = await self.db.execute(
            select(Spo2Reading).where(Spo2Reading.user_id == user_id).order_by(
                desc(Spo2Reading.recorded_at)
            ).limit(1)
        )
        latest_sleep = await self.db.execute(
            select(SleepSession).where(SleepSession.user_id == user_id).order_by(
                desc(SleepSession.started_at)
            ).limit(1)
        )
        latest_stress = await self.db.execute(
            select(StressReading).where(StressReading.user_id == user_id).order_by(
                desc(StressReading.recorded_at)
            ).limit(1)
        )
        steps_today = await self.db.execute(
            select(func.coalesce(func.sum(ActivityReading.steps), 0)).where(
                ActivityReading.user_id == user_id
            )
        )
        return {
            "latest_heart_rate": getattr(latest_hr.scalars().first(), "bpm", None),
            "latest_spo2": getattr(latest_spo2.scalars().first(), "percentage", None),
            "steps_today": int(steps_today.scalar_one() or 0),
            "sleep_minutes_latest": getattr(latest_sleep.scalars().first(), "duration_minutes", None),
            "stress_latest": getattr(latest_stress.scalars().first(), "score", None),
        }

    model_map = {
        "heart-rate": HeartRateReading,
        "hrv": HrvReading,
        "spo2": Spo2Reading,
        "activity": ActivityReading,
        "stress": StressReading,
        "temperature": SkinTemperatureReading,
    }

