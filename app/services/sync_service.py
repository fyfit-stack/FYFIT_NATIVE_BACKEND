from datetime import timezone
import uuid

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
        if payload.device_id:
            device = await self.devices.require_owned(user, payload.device_id)
        else:
            devices = await self.devices.list_for_user(user)
            if not devices:
                from app.schemas.device import DevicePairRequest
                device = await self.devices.pair(user, DevicePairRequest(
                    serial_number="auto-created-sn",
                    device_type="smartring",
                    model="Auto-Paired Ring",
                    firmware_version="1.0",
                ))
            else:
                device = devices[0]
        parser = get_parser(device.model)

        inserted: dict[str, int] = {}
        skipped: dict[str, int] = {}

        inserted["heart_rate"] = await self.health.bulk_add(
            [
                HeartRateReading(
                    user_id=user.id,
                    device_id=device.id,
                    measured_at=item.recorded_at,
                    bpm=int(normalized.heart_rate),
                    reading_type=item.data.get("reading_type", "continuous"),
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
                    measured_at=item.recorded_at,
                    rmssd_ms=float(normalized.hrv),
                    reading_type=item.data.get("reading_type", "continuous"),
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
                    measured_at=item.recorded_at,
                    spo2_pct=float(normalized.spo2),
                    reading_type=item.data.get("reading_type", "continuous"),
                )
                for item, normalized in self._normalized(parser, payload.spo2)
                if normalized.spo2 is not None
            ]
        )
        skipped["spo2"] = len(payload.spo2) - inserted["spo2"]

        activity_rows = [
            ActivityReading(
                id=uuid.uuid4(),
                user_id=user.id,
                device_id=device.id,
                recorded_date=item.recorded_at.date(),
                steps=normalized.steps,
                calories_burned=normalized.calories_kcal,
                distance_km=(normalized.distance_meters / 1000.0) if normalized.distance_meters is not None else None,
                active_minutes=normalized.active_minutes,
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
        
        if activity_rows:
            inserted["activity"] = await self.health.upsert_activity_readings(activity_rows)
        else:
            inserted["activity"] = 0
            
        skipped["activity"] = len(payload.activity) - inserted["activity"]

        inserted["stress"] = await self.health.bulk_add(
            [
                StressReading(
                    user_id=user.id,
                    device_id=device.id,
                    measured_at=item.recorded_at,
                    stress_score=int(normalized.stress),
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
                    measured_at=item.recorded_at,
                    temperature_c=float(normalized.skin_temperature_celsius),
                )
                for item, normalized in self._normalized(parser, payload.temperature)
                if normalized.skin_temperature_celsius is not None
            ]
        )
        skipped["temperature"] = len(payload.temperature) - inserted["temperature"]

        sleep_rows = [
            SleepSession(
                id=uuid.uuid4(),
                user_id=user.id,
                device_id=device.id,
                sleep_start=item.started_at,
                sleep_end=item.ended_at,
                total_sleep_min=int((item.ended_at - item.started_at).total_seconds() // 60),
                deep_sleep_min=item.data.get("deep_sleep_min", 0),
                light_sleep_min=item.data.get("light_sleep_min", 0),
                rem_sleep_min=item.data.get("rem_sleep_min", 0),
                awake_min=item.data.get("awake_min", 0),
                sleep_score=item.data.get("score"),
                recorded_date=item.ended_at.date(),
            )
            for item in payload.sleep
        ]
        inserted["sleep"] = 0
        if sleep_rows:
            inserted["sleep"] = await self.health.upsert_sleep_sessions(sleep_rows)
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

