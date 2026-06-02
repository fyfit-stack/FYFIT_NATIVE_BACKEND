from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_notifications():
    return {"message": "Notification preferences and queue endpoints scaffolded."}

