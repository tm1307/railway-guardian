from fastapi import APIRouter, Depends
from ....services.intent_service import intent_service
from ....core.security import get_current_user

router = APIRouter()

@router.get("/predictions")
async def get_predictions(user: dict = Depends(get_current_user)):
    return intent_service.get_predictions()

@router.get("/timeline")
async def get_timeline(user: dict = Depends(get_current_user)):
    return intent_service.get_timeline()
