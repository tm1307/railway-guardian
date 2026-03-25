from fastapi import APIRouter, Depends
from ....services.predictive_failure import predictive_engine
from ....core.security import get_current_user

router = APIRouter()


@router.get("/health")
async def get_track_health(user: dict = Depends(get_current_user)):
    """Get per-section track health with predicted failure dates."""
    return predictive_engine.get_section_health()


@router.get("/anomalies")
async def get_anomalies(user: dict = Depends(get_current_user)):
    """Get detected vibration anomalies via EWMA analysis."""
    return predictive_engine.get_anomalies()
