from typing import Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id_) -> ModelT | None:
        return await self.db.get(self.model, id_)

    async def list(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        result = await self.db.execute(select(self.model).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def first(self, statement: Select) -> ModelT | None:
        result = await self.db.execute(statement)
        return result.scalars().first()

