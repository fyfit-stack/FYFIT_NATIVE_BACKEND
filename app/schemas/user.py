from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.common import TimestampedSchema


class UserSchema(TimestampedSchema):
    firebase_uid: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    profile_pic_url: str | None = None
    id: UUID

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    phone: str | None = Field(None, pattern=r"^\+?[\d\s-]{10,15}$")

class UserProfileUpsert(BaseModel):
    first_name: str | None = None
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
    email: EmailStr | None = None

