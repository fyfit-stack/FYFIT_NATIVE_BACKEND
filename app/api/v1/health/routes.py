from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.health import HealthSummary
from app.services.health_service import HealthService

router = APIRouter()


@router.get("/summary", response_model=HealthSummary)
async def summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await HealthService(db).summary(current_user)


async def _metric(
    metric: str,
    current_user: User,
    db: AsyncSession,
    start: datetime | None,
    end: datetime | None,
    limit: int,
    offset: int,
):
    return await HealthService(db).readings(
        current_user, metric, start=start, end=end, limit=limit, offset=offset
    )


@router.get("/heart-rate")
async def heart_rate(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
):
    return await _metric("heart-rate", current_user, db, start, end, limit, offset)


@router.get("/hrv")
async def hrv(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
):
    return await _metric("hrv", current_user, db, start, end, limit, offset)


@router.get("/spo2")
async def spo2(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
):
    return await _metric("spo2", current_user, db, start, end, limit, offset)


@router.get("/activity")
async def activity(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
):
    return await _metric("activity", current_user, db, start, end, limit, offset)


@router.get("/stress")
async def stress(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
):
    return await _metric("stress", current_user, db, start, end, limit, offset)


@router.get("/sleep")
async def sleep():
    return {"message": "Sleep session endpoint scaffolded; add repository pagination as needed."}


@router.get("/workouts")
async def workouts():
    return {"message": "Workout endpoint scaffolded; add repository pagination as needed."}


@router.get("/goals")
async def goals():
    return {"message": "Goal endpoint scaffolded; see /api/v1/goals."}

