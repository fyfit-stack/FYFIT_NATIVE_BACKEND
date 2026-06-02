from uuid import UUID

from sqlalchemy import select

from app.models.user import User, UserHealthProfile
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        return await self.first(select(User).where(User.firebase_uid == firebase_uid))


class UserHealthProfileRepository(BaseRepository[UserHealthProfile]):
    model = UserHealthProfile

    async def get_by_user_id(self, user_id: UUID) -> UserHealthProfile | None:
        return await self.first(select(UserHealthProfile).where(UserHealthProfile.user_id == user_id))
