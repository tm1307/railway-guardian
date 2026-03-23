"""
Maintenance Scheduling Service
CRUD operations for maintenance schedules + active window checking for alert suppression.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.models import MaintenanceSchedule
import logging

logger = logging.getLogger(__name__)

class MaintenanceManager:
    def get_active_schedules(self, db: Session):
        """Get currently active maintenance windows."""
        now = datetime.utcnow()
        return db.query(MaintenanceSchedule).filter(
            MaintenanceSchedule.is_active == True,
            MaintenanceSchedule.start_time <= now,
            MaintenanceSchedule.end_time >= now,
        ).all()

    def get_all_schedules(self, db: Session):
        """Get all maintenance schedules."""
        return db.query(MaintenanceSchedule).order_by(
            MaintenanceSchedule.start_time.desc()
        ).all()

    def is_maintenance_active(self, db: Session, section: str = None):
        """Check if maintenance is active (optionally for a section)."""
        active = self.get_active_schedules(db)
        if section:
            return any(s.section == section for s in active)
        return len(active) > 0

    def get_active_sections(self, db: Session):
        """Get list of section names currently under maintenance."""
        active = self.get_active_schedules(db)
        return [s.section for s in active]

    def create_schedule(self, db: Session, data: dict):
        """Create a new maintenance schedule."""
        schedule = MaintenanceSchedule(
            section=data["section"],
            task=data["task"],
            team=data.get("team", "General"),
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            is_active=data.get("is_active", True),
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule

    def update_schedule(self, db: Session, schedule_id: int, data: dict):
        """Update an existing schedule."""
        sched = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == schedule_id).first()
        if not sched:
            return None
        for key, val in data.items():
            if key in ("section", "task", "team", "is_active"):
                setattr(sched, key, val)
            elif key == "start_time":
                sched.start_time = datetime.fromisoformat(val)
            elif key == "end_time":
                sched.end_time = datetime.fromisoformat(val)
        db.commit()
        db.refresh(sched)
        return sched

    def delete_schedule(self, db: Session, schedule_id: int):
        """Delete a schedule."""
        sched = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == schedule_id).first()
        if sched:
            db.delete(sched)
            db.commit()
            return True
        return False

    def toggle_active(self, db: Session, schedule_id: int):
        """Toggle schedule active status."""
        sched = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == schedule_id).first()
        if sched:
            sched.is_active = not sched.is_active
            db.commit()
            return sched
        return None


maintenance_manager = MaintenanceManager()
