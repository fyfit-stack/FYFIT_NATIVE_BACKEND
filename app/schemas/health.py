from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DateRangeQuery(BaseModel):
    start: datetime | None = None
    end: datetime | None = None
    limit: int = 100
    offset: int = 0


class HealthSummary(BaseModel):
    latest_heart_rate: int | None = None
    latest_spo2: float | None = None
    steps_today: int = 0
    sleep_minutes_latest: int | None = None
    stress_latest: int | None = None


class HeartRateResponse(BaseModel):
    id: int
    measured_at: datetime
    bpm: int
    reading_type: str
    class Config:
        from_attributes = True

class Spo2Response(BaseModel):
    id: int
    measured_at: datetime
    spo2_pct: float
    reading_type: str
    class Config:
        from_attributes = True

class HrvResponse(BaseModel):
    id: int
    measured_at: datetime
    rmssd_ms: float
    reading_type: str
    class Config:
        from_attributes = True

class StressResponse(BaseModel):
    id: int
    measured_at: datetime
    stress_score: int
    class Config:
        from_attributes = True

class TempResponse(BaseModel):
    id: int
    measured_at: datetime
    temperature_c: float
    baseline_c: float | None = None
    deviation_c: float | None = None
    class Config:
        from_attributes = True

from datetime import date

class SleepSessionResponse(BaseModel):
    id: UUID
    sleep_start: datetime
    sleep_end: datetime
    total_sleep_min: int
    deep_sleep_min: int | None = 0
    light_sleep_min: int | None = 0
    rem_sleep_min: int | None = 0
    awake_min: int | None = 0
    sleep_score: int | None = None
    recorded_date: date

    class Config:
        from_attributes = True

class ActivityResponse(BaseModel):
    id: UUID
    recorded_date: date
    steps: int | None = 0
    distance_km: float | None = 0
    calories_burned: float | None = 0
    active_minutes: int | None = 0
    sedentary_min: int | None = 0

    class Config:
        from_attributes = True

