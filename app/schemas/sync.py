from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RawReading(BaseModel):
    recorded_at: datetime
    data: dict = Field(default_factory=dict)


class RawSleepSession(BaseModel):
    started_at: datetime
    ended_at: datetime
    data: dict = Field(default_factory=dict)


class BatchSyncRequest(BaseModel):
    device_id: UUID | None = None
    heart_rate: list[RawReading] = Field(default_factory=list)
    hrv: list[RawReading] = Field(default_factory=list)
    spo2: list[RawReading] = Field(default_factory=list)
    activity: list[RawReading] = Field(default_factory=list)
    sleep: list[RawSleepSession] = Field(default_factory=list)
    stress: list[RawReading] = Field(default_factory=list)
    temperature: list[RawReading] = Field(default_factory=list)
    workouts: list[dict] = Field(default_factory=list)


class BatchSyncResult(BaseModel):
    device_id: UUID
    inserted: dict[str, int]
    skipped: dict[str, int]


class NormalizedReading(BaseModel):
    recorded_at: datetime
    heart_rate: int | None = None
    hrv: float | None = None
    spo2: float | None = None
    steps: int | None = None
    stress: int | None = None
    skin_temperature_celsius: float | None = None
    calories_kcal: float | None = None
    distance_meters: float | None = None
    active_minutes: int | None = None
    source_payload: dict | None = None

