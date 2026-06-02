from datetime import timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.devices.registry import get_parser
from app.models.device import Device
from app.models.health import (
    ActivityReading,
    HeartRateReading,
    HrvReading,
    SkinTemperatureReading,
    SleepSession,
    Spo2Reading,
    StressReading,
)
from app.models.user import User
from app.repositories.health_repository import HealthRepository
from app.schemas.sync import BatchSyncRequest, BatchSyncResult, RawReading
from app.services.device_service import DeviceService


class SyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.health = HealthRepository(db)
        self.devices = DeviceService(db)

    async def sync_batch(self, user: User, payload: BatchSyncRequest) -> BatchSyncResult:
        device = await self.devices.require_owned(user, payload.device_id)
        parser = get_parser(device.model)

        inserted: dict[str, int] = {}
        skipped: dict[str, int] = {}

        inserted["heart_rate"] = await self.health.bulk_add(
            [
                HeartRateReading(
                    user_id=user.id,
                    device_id=device.id,
                    recorded_at=item.recorded_at,
                    bpm=int(normalized.heart_rate),
                    source_payload=item.data,
                )
                for item, normalized in self._normalized(parser, payload.heart_rate)
                if normalized.heart_rate is not None
            ]
        )
        skipped["heart_rate"] = len(payload.heart_rate) - inserted["heart_rate"]

        inserted["hrv"] = await self.health.bulk_add(
            [
                HrvReading(
                    user_id=user.id,
                    device_id=device.id,
                    recorded_at=item.recorded_at,
                    rmssd_ms=float(normalized.hrv),
                    source_payload=item.data,
                )
                for item, normalized in self._normalized(parser, payload.hrv)
                if normalized.hrv is not None
            ]
        )
        skipped["hrv"] = len(payload.hrv) - inserted["hrv"]

        inserted["spo2"] = await self.health.bulk_add(
            [
                Spo2Reading(
                    user_id=user.id,
                    device_id=device.id,
                    recorded_at=item.recorded_at,
                    percentage=float(normalized.spo2),
                    source_payload=item.data,
                )
                for item, normalized in self._normalized(parser, payload.spo2)
                if normalized.spo2 is not None
            ]
        )
        skipped["spo2"] = len(payload.spo2) - inserted["spo2"]

        inserted["activity"] = await self.health.bulk_add(
            [
                ActivityReading(
                    user_id=user.id,
                    device_id=device.id,
                    recorded_at=item.recorded_at,
                    steps=normalized.steps,
                    calories_kcal=normalized.calories_kcal,
                    distance_meters=normalized.distance_meters,
                    active_minutes=normalized.active_minutes,
                    source_payload=item.data,
                )
                for item, normalized in self._normalized(parser, payload.activity)
                if any(
                    value is not None
                    for value in (
                        normalized.steps,
                        normalized.calories_kcal,
                        normalized.distance_meters,
                        normalized.active_minutes,
                    )
                )
            ]
        )
        skipped["activity"] = len(payload.activity) - inserted["activity"]

        inserted["stress"] = await self.health.bulk_add(
            [
                StressReading(
                    user_id=user.id,
                    device_id=device.id,
                    recorded_at=item.recorded_at,
                    score=int(normalized.stress),
                    source_payload=item.data,
                )
                for item, normalized in self._normalized(parser, payload.stress)
                if normalized.stress is not None
            ]
        )
        skipped["stress"] = len(payload.stress) - inserted["stress"]

        inserted["temperature"] = await self.health.bulk_add(
            [
                SkinTemperatureReading(
                    user_id=user.id,
                    device_id=device.id,
                    recorded_at=item.recorded_at,
                    celsius=float(normalized.skin_temperature_celsius),
                    source_payload=item.data,
                )
                for item, normalized in self._normalized(parser, payload.temperature)
                if normalized.skin_temperature_celsius is not None
            ]
        )
        skipped["temperature"] = len(payload.temperature) - inserted["temperature"]

        sleep_rows = [
            SleepSession(
                user_id=user.id,
                device_id=device.id,
                started_at=item.started_at,
                ended_at=item.ended_at,
                duration_minutes=int((item.ended_at - item.started_at).total_seconds() // 60),
                score=item.data.get("score"),
                stages=item.data.get("stages"),
                source_payload=item.data,
            )
            for item in payload.sleep
        ]
        inserted["sleep"] = await self.health.bulk_add(sleep_rows)
        skipped["sleep"] = len(payload.sleep) - inserted["sleep"]

        await self.devices.mark_synced(device)
        await self.db.commit()
        return BatchSyncResult(device_id=device.id, inserted=inserted, skipped=skipped)

    @staticmethod
    def _normalized(parser, readings: list[RawReading]):
        for item in readings:
            recorded_at = item.recorded_at
            if recorded_at.tzinfo is None:
                recorded_at = recorded_at.replace(tzinfo=timezone.utc)
            yield item, parser.normalize_reading(recorded_at, item.data)

