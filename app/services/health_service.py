from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, db: AsyncSession):
        self.health = HealthRepository(db)

    async def summary(self, user: User) -> dict:
        return await self.health.summary(user.id)

    async def readings(
        self,
        user: User,
        metric: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list:
        model = self.health.model_map[metric]
        return await self.health.readings(model, user.id, start=start, end=end, limit=limit, offset=offset)

