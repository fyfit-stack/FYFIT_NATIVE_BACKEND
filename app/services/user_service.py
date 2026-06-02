from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserHealthProfile
from app.repositories.user_repository import UserHealthProfileRepository, UserRepository
from app.schemas.user import UserProfileUpsert


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)
        self.profiles = UserHealthProfileRepository(db)

    async def get_or_create_from_firebase(self, token: dict) -> User:
        firebase_uid = token["uid"]
        user = await self.users.get_by_firebase_uid(firebase_uid)
        if user:
            return user

        user = User(
            firebase_uid=firebase_uid,
            email=token.get("email"),
            display_name=token.get("name"),
            photo_url=token.get("picture"),
        )
        await self.users.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def upsert_profile(self, user: User, payload: UserProfileUpsert) -> UserHealthProfile:
        profile = await self.profiles.get_by_user_id(user.id) or UserHealthProfile(user_id=user.id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
