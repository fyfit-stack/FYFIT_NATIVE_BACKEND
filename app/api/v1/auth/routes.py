from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import UserSchema, UserCreate, Token, LoginRequest
from app.services.user_service import UserService

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    if user_in.phone:
        result_phone = await db.execute(select(User).where(User.phone == user_in.phone))
        if result_phone.scalars().first():
            raise HTTPException(status_code=400, detail="Phone number already registered")

    new_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        first_name=user_in.full_name, # Note: storing full name in first_name for now
        phone=user_in.phone
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    access_token = create_access_token(subject=str(new_user.id))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().first()
    
    if not user or not user.password_hash:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
