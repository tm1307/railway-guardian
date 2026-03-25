from fastapi import APIRouter, Depends
from ....services.weather_service import weather_service
from ....core.security import get_current_user

router = APIRouter()

@router.get("/current")
async def get_current_weather(user: dict = Depends(get_current_user)):
    return await weather_service.get_current()

@router.get("/forecast")
async def get_forecast(user: dict = Depends(get_current_user)):
    return await weather_service.get_forecast()

@router.get("/rail-impact")
async def get_rail_impact(user: dict = Depends(get_current_user)):
    return await weather_service.get_rail_impact()
