from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from ....db.session import get_db
from ....core.security import get_current_user, require_role
from ....core.sockets import send_alert
from ....services.maintenance import maintenance_manager

router = APIRouter()

# ─── Maintenance CRUD ──────────────────────────────────────────────

class ScheduleCreate(BaseModel):
    section: str
    task: str
    team: str = "General"
    start_time: str  # ISO format
    end_time: str
    is_active: bool = True

class ScheduleUpdate(BaseModel):
    section: Optional[str] = None
    task: Optional[str] = None
    team: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/schedules")
async def list_schedules(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    schedules = maintenance_manager.get_all_schedules(db)
    now = datetime.utcnow()
    return [{
        "id": s.id,
        "section": s.section,
        "task": s.task,
        "team": s.team,
        "start_time": s.start_time.isoformat() if s.start_time else None,
        "end_time": s.end_time.isoformat() if s.end_time else None,
        "is_active": s.is_active,
        "status": "in_progress" if s.is_active and s.start_time <= now <= s.end_time else
                  "completed" if s.end_time < now else
                  "scheduled" if s.start_time > now else "inactive",
    } for s in schedules]

@router.get("/active")
async def get_active_maintenance(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    active = maintenance_manager.get_active_schedules(db)
    return [{
        "id": s.id, "section": s.section, "task": s.task, "team": s.team,
        "start_time": s.start_time.isoformat(), "end_time": s.end_time.isoformat(),
    } for s in active]

@router.post("/schedules")
async def create_schedule(data: ScheduleCreate, user: dict = Depends(require_role("admin", "operator")), db: Session = Depends(get_db)):
    sched = maintenance_manager.create_schedule(db, data.dict())
    return {
        "id": sched.id, "section": sched.section, "task": sched.task,
        "message": "Schedule created successfully"
    }

@router.put("/schedules/{schedule_id}")
async def update_schedule(schedule_id: int, data: ScheduleUpdate, user: dict = Depends(require_role("admin", "operator")), db: Session = Depends(get_db)):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    sched = maintenance_manager.update_schedule(db, schedule_id, update_data)
    if not sched:
        return {"error": "Schedule not found"}
    return {"id": sched.id, "message": "Schedule updated"}

@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int, user: dict = Depends(require_role("admin")), db: Session = Depends(get_db)):
    ok = maintenance_manager.delete_schedule(db, schedule_id)
    return {"deleted": ok}

@router.post("/schedules/{schedule_id}/toggle")
async def toggle_schedule(schedule_id: int, user: dict = Depends(require_role("admin", "operator")), db: Session = Depends(get_db)):
    sched = maintenance_manager.toggle_active(db, schedule_id)
    if not sched:
        return {"error": "Not found"}
    return {"id": sched.id, "is_active": sched.is_active}

# ─── Operator Manual Alert ─────────────────────────────────────────

class ManualAlert(BaseModel):
    alert_type: str
    severity: str = "high"
    message: str
    location: str = ""

@router.post("/alert")
async def send_manual_alert(data: ManualAlert, user: dict = Depends(require_role("admin", "operator"))):
    """Operators/admins can send manual alerts that broadcast to all connected clients."""
    alert = {
        "id": int(datetime.utcnow().timestamp() * 1000),
        "node_id": data.location or "MANUAL",
        "node_name": data.location or "Operator Report",
        "alert_type": data.alert_type,
        "severity": data.severity,
        "risk_score": {"critical": 90, "high": 70, "medium": 45, "low": 20}.get(data.severity, 50),
        "explanation": f"[{user['username'].upper()}] {data.message}",
        "timestamp": datetime.utcnow().isoformat(),
        "source": "OPERATOR_MANUAL",
        "reported_by": user["username"],
    }
    await send_alert(alert)
    return {"status": "alert_sent", "alert": alert}
