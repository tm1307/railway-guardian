from fastapi import APIRouter, Depends
from ....services.risk_service import risk_service
from ....core.security import get_current_user

router = APIRouter()

@router.get("/heatmap")
async def get_heatmap(user: dict = Depends(get_current_user)):
    return risk_service.get_heatmap_data()

@router.get("/scores")
async def get_scores(user: dict = Depends(get_current_user)):
    return risk_service.get_ranked_scores()
