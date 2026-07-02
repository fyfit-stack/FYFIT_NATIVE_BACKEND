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

    async def upsert_sleep_sessions(self, sessions: list[SleepSession]) -> int:
        if not sessions:
            return 0
        
        from sqlalchemy.dialects.postgresql import insert
        
        inserted_count = 0
        for session in sessions:
            stmt = insert(SleepSession).values(
                id=session.id,
                user_id=session.user_id,
                device_id=session.device_id,
                sleep_start=session.sleep_start,
                sleep_end=session.sleep_end,
                total_sleep_min=session.total_sleep_min,
                deep_sleep_min=session.deep_sleep_min,
                rem_sleep_min=session.rem_sleep_min,
                light_sleep_min=session.light_sleep_min,
                awake_min=session.awake_min,
                sleep_score=session.sleep_score,
                recorded_date=session.recorded_date,
            )
            
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_id', 'recorded_date'],
                set_={
                    'sleep_start': stmt.excluded.sleep_start,
                    'sleep_end': stmt.excluded.sleep_end,
                    'total_sleep_min': stmt.excluded.total_sleep_min,
                    'deep_sleep_min': stmt.excluded.deep_sleep_min,
                    'rem_sleep_min': stmt.excluded.rem_sleep_min,
                    'light_sleep_min': stmt.excluded.light_sleep_min,
                    'awake_min': stmt.excluded.awake_min,
                    'sleep_score': stmt.excluded.sleep_score,
                }
            )
            
            await self.db.execute(stmt)
            inserted_count += 1
            
        await self.db.flush()
        return inserted_count

    async def upsert_activity_readings(self, readings: list[ActivityReading]) -> int:
        if not readings:
            return 0
        
        from sqlalchemy.dialects.postgresql import insert
        
        inserted_count = 0
        for reading in readings:
            stmt = insert(ActivityReading).values(
                id=reading.id,
                user_id=reading.user_id,
                device_id=reading.device_id,
                recorded_date=reading.recorded_date,
                steps=reading.steps,
                distance_km=reading.distance_km,
                calories_burned=reading.calories_burned,
                active_minutes=reading.active_minutes,
                sedentary_min=reading.sedentary_min,
                floors_climbed=reading.floors_climbed,
                elevation_m=reading.elevation_m,
                hourly_steps=reading.hourly_steps,
            )
            
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_id', 'device_id', 'recorded_date'],
                set_={
                    'steps': stmt.excluded.steps,
                    'distance_km': stmt.excluded.distance_km,
                    'calories_burned': stmt.excluded.calories_burned,
                    'active_minutes': stmt.excluded.active_minutes,
                    'sedentary_min': stmt.excluded.sedentary_min,
                    'floors_climbed': stmt.excluded.floors_climbed,
                    'elevation_m': stmt.excluded.elevation_m,
                    'hourly_steps': stmt.excluded.hourly_steps,
                }
            )
            
            await self.db.execute(stmt)
            inserted_count += 1
            
        await self.db.flush()
        return inserted_count

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
        # Determine the correct datetime column based on the model
        time_col = getattr(model, "measured_at", None)
        if time_col is None:
            time_col = getattr(model, "recorded_date", None)
            
        statement: Select = select(model).where(model.user_id == user_id)
        if start:
            statement = statement.where(time_col >= start)
        if end:
            statement = statement.where(time_col <= end)
        result = await self.db.execute(
            statement.order_by(desc(time_col)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def sleep_sessions(
        self,
        user_id: UUID,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SleepSession]:
        statement: Select = select(SleepSession).where(SleepSession.user_id == user_id)
        if start:
            statement = statement.where(SleepSession.sleep_start >= start)
        if end:
            statement = statement.where(SleepSession.sleep_start <= end)
        result = await self.db.execute(
            statement.order_by(desc(SleepSession.sleep_start)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def summary(self, user_id: UUID) -> dict:
        latest_hr = await self.db.execute(
            select(HeartRateReading).where(HeartRateReading.user_id == user_id).order_by(
                desc(HeartRateReading.measured_at)
            ).limit(1)
        )
        latest_spo2 = await self.db.execute(
            select(Spo2Reading).where(Spo2Reading.user_id == user_id).order_by(
                desc(Spo2Reading.measured_at)
            ).limit(1)
        )
        latest_sleep = await self.db.execute(
            select(SleepSession).where(SleepSession.user_id == user_id).order_by(
                desc(SleepSession.sleep_start)
            ).limit(1)
        )
        latest_stress = await self.db.execute(
            select(StressReading).where(StressReading.user_id == user_id).order_by(
                desc(StressReading.measured_at)
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
            "sleep_minutes_latest": getattr(latest_sleep.scalars().first(), "total_sleep_min", None),
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

