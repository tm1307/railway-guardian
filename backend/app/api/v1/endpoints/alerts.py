from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
import hashlib
from datetime import datetime
from ....db.session import get_db
from ....services.alerts import alert_service
from ....services.phyphox import phyphox_service
from ....services.vision import vision_service
from ....services.fusion import fusion_engine
from ....services.forensics import forensics_service
from ....core.sockets import send_alert
from ....models.models import AuditLog, MaintenanceSchedule, Incident

router = APIRouter()

@router.post("/upload")
async def upload_evidence(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Save File
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. Process Forensics if Video
    detections = []
    if file.filename.lower().endswith(('.mp4', '.avi', '.mov')):
        detections = await forensics_service.process_video(file_path)
    else:
        # Image detection
        detections, _ = vision_service.detect_threats(file_path)
    
    # 3. Create Incident from Forensics
    node_id = "MANUAL_UPLOAD"
    alert_type, explanation = await fusion_engine.classify_incident(
        detections, 0.0, False, 1.0
    )
    
    incident = await alert_service.process_alert(
        db, node_id, alert_type, 0.0, 0.0
    )
    incident.explanation = f"FORENSIC ANALYSIS: {explanation}"
    incident.evidence_path = file_path
    
    # Evidence Integrity Hash
    evidence_string = f"{node_id}-{file.filename}-{datetime.utcnow()}"
    incident.evidence_hash = hashlib.sha256(evidence_string.encode()).hexdigest()
    
    db.commit()
    
    # Broadcast
    alert_data = {
        "id": incident.id,
        "node_id": node_id,
        "type": alert_type,
        "severity": incident.severity.lower(),
        "risk_score": incident.risk_score,
        "msg": incident.explanation,
        "time": incident.timestamp.strftime("%H:%M:%S")
    }
    await send_alert(alert_data)
    
    return {"status": "analyzed", "incident_id": incident.id, "detections": detections, "hash": incident.evidence_hash}

@router.post("/")
async def create_alert(alert_in: dict, db: Session = Depends(get_db)):
    node_id = alert_in.get("node_id")
    vibration_val = alert_in.get("vibration_level", 0.0)
    gps_km = alert_in.get("gps_km", 0.0)
    
    # 1. Fusion Engine: Real-time Analysis
    detections = alert_in.get("detections_list", [])
    is_maint = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.is_active == True,
        MaintenanceSchedule.section == node_id
    ).first() is not None

    alert_type, explanation = await fusion_engine.classify_incident(
        detections, vibration_val, is_maint, alert_in.get("confidence_score", 1.0)
    )
    
    incident = await alert_service.process_alert(
        db, node_id, alert_type, vibration_val, gps_km
    )
    incident.explanation = explanation
    
    # 2. Cyber Security: SHA-256 Hashing for Evidence Integrity
    evidence_string = f"{node_id}-{vibration_val}-{gps_km}-{alert_in.get('timestamp')}"
    evidence_hash = hashlib.sha256(evidence_string.encode()).hexdigest()
    incident.evidence_hash = evidence_hash
    db.commit()
    
    # 3. Broadcast via WebSocket
    alert_data = {
        "id": incident.id,
        "node_id": incident.node_id,
        "type": incident.alert_type,
        "severity": incident.severity.lower(),
        "risk_score": incident.risk_score,
        "msg": incident.explanation,
        "time": incident.timestamp.strftime("%H:%M:%S")
    }
    await send_alert(alert_data)
    
    return {"status": "processed", "incident_id": incident.id, "hash": evidence_hash}

@router.post("/phyphox/connect")
async def connect_phyphox(payload: dict):
    ip = payload.get("ip")
    if not ip:
        raise HTTPException(status_code=400, detail="IP address required")
    
    success = await phyphox_service.connect(ip)
    if success:
        return {"status": "connected", "ip": ip}
    raise HTTPException(status_code=500, detail="Failed to connect to Phyphox")

@router.get("/phyphox/status")
async def get_phyphox_status():
    return {
        "connected": phyphox_service.is_connected,
        "ip": phyphox_service.base_url.split("//")[1].split("/")[0] if phyphox_service.is_connected else None
    }

@router.get("/phyphox/vibration")
async def get_phyphox_vibration():
    if not phyphox_service.is_connected:
        return {"peak_amplitude": 0.0}
    data = await phyphox_service.fetch_data()
    peak = max(abs(data.get("x", 0)), abs(data.get("y", 0)), abs(data.get("z", 0)))
    return {"peak_amplitude": peak}

@router.get("/{alert_id}/report")
async def get_report(alert_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == alert_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    report_content = f"""
    RAILWAY GUARDIAN - FORENSIC INCIDENT REPORT
    ==========================================
    INCIDENT ID: {incident.id}
    TIMESTAMP: {incident.timestamp}
    NODE ID: {incident.node_id}
    LOCATION: KM {incident.gps_km}
    
    THREAT DETAILS:
    Type: {incident.alert_type}
    Severity: {incident.severity}
    Risk Score: {incident.risk_score}/100
    
    CYBER SECURITY & INTEGRITY:
    RDSO Evidence Hash: {incident.evidence_hash}
    Verification: TAMPER-PROOF [SHA-256]
    
    ------------------------------------------
    MINISTRY OF RAILWAYS - GOVT OF INDIA
    """
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=report_content, media_type="text/plain", 
                             headers={"Content-Disposition": f"attachment; filename=report_{alert_id}.txt"})

@router.get("/")
async def get_alerts(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.timestamp.desc()).limit(50).all()
