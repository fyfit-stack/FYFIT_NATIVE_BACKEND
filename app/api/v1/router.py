from fastapi import APIRouter

from app.api.v1.ai.routes import router as ai_router
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.devices.routes import router as devices_router
from app.api.v1.goals.routes import router as goals_router
from app.api.v1.health.routes import router as health_router
from app.api.v1.notifications.routes import router as notifications_router
from app.api.v1.sync.routes import router as sync_router
from app.api.v1.users.routes import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(devices_router, prefix="/devices", tags=["devices"])
api_router.include_router(sync_router, prefix="/sync", tags=["sync"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(goals_router, prefix="/goals", tags=["goals"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])

