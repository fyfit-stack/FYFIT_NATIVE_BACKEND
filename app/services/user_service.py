from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserHealthProfile
from app.repositories.user_repository import UserHealthProfileRepository, UserRepository
from app.schemas.user import UserProfileUpsert


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)
        self.profiles = UserHealthProfileRepository(db)

    async def get_by_id(self, user_id) -> User | None:
        return await self.users.get(user_id)

    async def get_or_create_from_firebase(self, token: dict) -> User:
        firebase_uid = token["uid"]
        user = await self.users.get_by_firebase_uid(firebase_uid)
        if user:
            return user

        user = User(
            firebase_uid=firebase_uid,
            email=token.get("email"),
            first_name=token.get("name"),
            profile_pic_url=token.get("picture"),
        )
        await self.users.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def upsert_profile(self, user: User, payload: UserProfileUpsert) -> UserHealthProfile:
        profile = await self.profiles.get_by_user_id(user.id) or UserHealthProfile(user_id=user.id)
        payload_data = payload.model_dump(exclude_unset=True)
        
        # Intercept User fields
        if "gender" in payload_data:
            user.gender = payload_data.pop("gender")
        if "date_of_birth" in payload_data:
            user.date_of_birth = payload_data.pop("date_of_birth")
        if "first_name" in payload_data:
            user.first_name = payload_data.pop("first_name")
            
        for key, value in payload_data.items():
            setattr(profile, key, value)
            
        self.db.add(profile)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
