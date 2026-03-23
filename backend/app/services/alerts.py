from sqlalchemy.orm import Session
from ..models.models import Incident
from .intelligence import intelligence_service
from .maintenance import maintenance_manager
import datetime

class AlertService:
    async def process_alert(self, db: Session, node_id: str, frame_data: bytes, vibration_val: float, gps_km: float):
        # 1. AI Analysis
        # Note: In production, we'd decode the frame_data
        # For now, we assume frame is processed by intelligence_service
        # (This would be handled in the endpoint)
        
        # 2. Maintenance Cross-Check
        # Assume section is derived from GPS
        section = f"section_{int(gps_km / 5) + 1}"
        is_maint = maintenance_manager.is_maintenance_active(db, section)
        maint_info = f"Active maintenance in {section}" if is_maint else "NONE"
        
        # 3. Final Risk Assessment (handled by intelligence_service + mock)
        # result = await intelligence_service.process_frame(frame, vibration_val)
        
        # Mocking the process for now
        alert_result = {
            "risk_score": 75.0 if vibration_val > 0.4 else 15.0,
            "vibration_status": "CRITICAL" if vibration_val > 0.4 else "STABLE",
            "detections": "person, bag" if vibration_val > 0.4 else "none",
            "severity": "CRITICAL" if vibration_val > 0.4 else "SAFE"
        }
        
        if is_maint:
            alert_result["risk_score"] *= 0.1
            alert_result["severity"] = "MAINTENANCE"
            alert_result["explanation"] = maint_info
        
        # 4. Save to Database
        incident = Incident(
            node_id=node_id,
            alert_type="SABOTAGE" if alert_result["risk_score"] > 70 else "NORMAL",
            severity=alert_result["severity"],
            risk_score=alert_result["risk_score"],
            vibration_level=vibration_val,
            detections=alert_result["detections"],
            gps_km=gps_km,
            maintenance_status=maint_info if is_maint else "NONE",
            timestamp=datetime.datetime.utcnow()
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        return incident

alert_service = AlertService()
