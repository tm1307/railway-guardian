from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from .api.v1.endpoints import alerts, auth, vision, weather, chatbot, risk, intent, infrastructure, sensors, maintenance, predictive
from .db.session import init_db
from .core.security import get_password_hash

app = FastAPI(title="Railway Guardian API", version="5.0.0")

@app.on_event("startup")
async def on_startup():
    init_db()
    _seed_data()
    
    # Start background scheduler for live updates
    from .services.scheduler import start_scheduler
    await start_scheduler()

def _seed_data():
    from .db.session import SessionLocal
    from .models.models import MaintenanceSchedule, User
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    
    # Seed users with different roles
    users_to_seed = [
        {"username": "admin", "password": "admin123", "full_name": "Chief Security Officer", "role": "admin"},
        {"username": "operator", "password": "operator123", "full_name": "Duty Controller", "role": "operator"},
        {"username": "viewer", "password": "viewer123", "full_name": "RPF Inspector", "role": "viewer"},
    ]
    
    for u in users_to_seed:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            db.add(User(
                username=u["username"],
                hashed_password=get_password_hash(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                is_active=True,
            ))
        else:
            existing.hashed_password = get_password_hash(u["password"])
            existing.role = u["role"]
    db.commit()
    
    # Seed maintenance schedules
    if not db.query(MaintenanceSchedule).first():
        schedules = [
            MaintenanceSchedule(section="NDLS-GZB", task="Track Polishing", team="Engineering Team A",
                              start_time=datetime.utcnow() - timedelta(hours=1),
                              end_time=datetime.utcnow() + timedelta(hours=5), is_active=True),
            MaintenanceSchedule(section="FDB-OKA", task="Signal Calibration", team="S&T Division",
                              start_time=datetime.utcnow() + timedelta(hours=2),
                              end_time=datetime.utcnow() + timedelta(hours=8), is_active=True),
        ]
        db.add_all(schedules)
        db.commit()
    db.close()

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(vision.router, prefix="/api/v1/vision", tags=["vision"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["risk"])
app.include_router(intent.router, prefix="/api/v1/intent", tags=["intent"])
app.include_router(infrastructure.router, prefix="/api/v1/infrastructure", tags=["infrastructure"])
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["sensors"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance", tags=["maintenance"])
app.include_router(predictive.router, prefix="/api/v1/predictive", tags=["predictive"])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .core.sockets import manager

@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "general"):
    await manager.connect(websocket, channel)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
