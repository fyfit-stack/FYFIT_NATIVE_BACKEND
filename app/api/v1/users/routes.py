import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserHealthProfileSchema, UserProfileUpsert
from app.services.user_service import UserService

router = APIRouter()


@router.patch("/profile", response_model=UserHealthProfileSchema)
async def upsert_profile(
    payload: UserProfileUpsert,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await UserService(db).upsert_profile(current_user, payload)

@router.get("/profile", response_model=UserHealthProfileSchema)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    profile = await UserService(db).profiles.get_by_user_id(current_user.id)
    
    # Merge user data with health profile
    data = {
        "user_id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "gender": current_user.gender,
        "date_of_birth": current_user.date_of_birth,
    }
    
    if profile:
        profile_data = {
            "id": profile.id,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "bmi": profile.bmi,
            "activity_level": profile.activity_level,
            "fitness_goal": profile.fitness_goal,
            "daily_step_goal": profile.daily_step_goal,
            "water_goal_ml": profile.daily_water_goal_ml,
            "sleep_goal_minutes": int(profile.sleep_goal_hours * 60) if profile.sleep_goal_hours else None,
            "target_weight_kg": profile.target_weight_kg,
            "baseline_hr": profile.resting_hr_baseline,
            "baseline_hrv": profile.hrv_baseline,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }
        data.update({k: v for k, v in profile_data.items() if v is not None})
    else:
        # Defaults if no profile exists
        data["id"] = uuid.uuid4()
        data["created_at"] = current_user.created_at
        data["updated_at"] = current_user.updated_at
        
    return UserHealthProfileSchema(**data)

