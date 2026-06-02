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


class ReadingOut(BaseModel):
    id: UUID
    recorded_at: datetime
    value: float | int | None
    unit: str

