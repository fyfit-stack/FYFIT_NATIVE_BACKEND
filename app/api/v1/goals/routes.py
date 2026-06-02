from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_goals():
    return {"message": "Goals API scaffolded for daily steps, water, sleep, and weight targets."}

