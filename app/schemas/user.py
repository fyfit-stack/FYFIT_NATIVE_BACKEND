from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.common import TimestampedSchema


class UserSchema(TimestampedSchema):
    firebase_uid: str
    email: EmailStr | None = None
    display_name: str | None = None
    photo_url: str | None = None


class UserProfileUpsert(BaseModel):
    gender: str | None = None
    date_of_birth: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    bmi: float | None = None
    activity_level: str | None = None
    fitness_goal: str | None = None
    daily_step_goal: int | None = None
    water_goal_ml: int | None = None
    sleep_goal_minutes: int | None = None
    target_weight_kg: float | None = None
    baseline_hr: int | None = None
    baseline_hrv: float | None = None


class UserHealthProfileSchema(UserProfileUpsert, TimestampedSchema):
    user_id: UUID

