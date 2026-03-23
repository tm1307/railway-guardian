from fastapi import APIRouter, Depends
from ....services.infrastructure_service import infrastructure_service
from ....core.security import get_current_user, require_role

router = APIRouter()

@router.get("/assets")
async def get_assets(user: dict = Depends(get_current_user)):
    return infrastructure_service.get_assets()

@router.get("/recommendations")
async def get_recommendations(user: dict = Depends(get_current_user)):
    return infrastructure_service.get_recommendations()

@router.post("/inspection")
async def log_inspection(payload: dict, user: dict = Depends(require_role("admin", "operator"))):
    return {
        "status": "logged",
        "asset_id": payload.get("asset_id"),
        "inspector": user["username"],
        "message": "Inspection record saved successfully."
    }
