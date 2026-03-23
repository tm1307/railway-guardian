from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ....core.security import get_current_user
from ....services.phyphox import phyphox_service
from ....services.scheduler import get_readings_history, get_phyphox_status
from datetime import datetime

router = APIRouter()

class PhyphoxConnectRequest(BaseModel):
    ip_address: str  # e.g. "192.168.1.5:8080"

@router.post("/phyphox/connect")
async def connect_phyphox(req: PhyphoxConnectRequest, user: dict = Depends(get_current_user)):
    """Connect to a real Phyphox phone sensor via IP."""
    success = await phyphox_service.connect(req.ip_address)
    return {
        "connected": success,
        "ip": req.ip_address,
        "message": "Connected! Live sensor data will now flow from your phone." if success else "Failed to connect. Ensure Phyphox is running and IP is correct."
    }

@router.get("/phyphox/status")
async def phyphox_status(user: dict = Depends(get_current_user)):
    """Check Phyphox connection status."""
    return get_phyphox_status()

@router.get("/phyphox/live")
async def phyphox_live(user: dict = Depends(get_current_user)):
    """Get latest real Phyphox reading."""
    if not phyphox_service.is_connected:
        return {"connected": False, "message": "Phyphox not connected. Use POST /phyphox/connect first."}
    data = await phyphox_service.fetch_data()
    return {"connected": True, "data": data, "timestamp": datetime.utcnow().isoformat()}

@router.get("/latest")
async def get_latest_readings(user: dict = Depends(get_current_user)):
    """Get latest sensor readings from actual stored history (not random)."""
    history = get_readings_history()
    if history:
        # Return last reading per node
        latest = {}
        for r in reversed(history):
            nid = r["node_id"]
            if nid not in latest:
                latest[nid] = r
            if len(latest) >= 6:
                break
        
        readings = []
        for nid, r in latest.items():
            for stype, val, unit in [
                ("vibration", r["vibration"], "g"),
                ("temperature", r["temperature"], "°C"),
                ("strain", r.get("strain", 0), "μɛ"),
                ("acoustic", r.get("acoustic", 0), "dB"),
            ]:
                status = "normal"
                if stype == "vibration" and val > 0.35:
                    status = "critical" if val > 0.45 else "warning"
                elif stype == "temperature" and val > 42:
                    status = "warning"
                elif stype == "strain" and val > 150:
                    status = "critical" if val > 180 else "warning"
                readings.append({
                    "node_id": nid,
                    "sensor_type": stype,
                    "value": val,
                    "unit": unit,
                    "status": status,
                    "timestamp": r["timestamp"],
                    "source": r.get("source", "SIMULATION"),
                })
        return readings
    
    # Fallback if no history yet
    return []

@router.get("/history")
async def get_sensor_history(sensor_type: str = "vibration", hours: int = 6, user: dict = Depends(get_current_user)):
    """Get sensor history from actual stored readings."""
    history = get_readings_history()
    field_map = {"vibration": "vibration", "temperature": "temperature", "strain": "strain", "acoustic": "acoustic"}
    field = field_map.get(sensor_type, "vibration")
    
    result = []
    for r in history:
        result.append({
            "timestamp": r["timestamp"],
            "value": r.get(field, 0),
            "node_id": r["node_id"],
            "source": r.get("source", "SIMULATION"),
        })
    return result[-200:]  # Last 200 readings
