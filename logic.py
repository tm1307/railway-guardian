"""
Fusion Engine & Risk Classification — Core AI logic for RailGuard.
Combines YOLOv8 vision + Isolation Forest vibration anomaly detection
into a multi-modal threat assessment with numerical risk scoring.
"""

import numpy as np
import joblib
import cv2
import requests
import os
import tempfile
from ultralytics import YOLO

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip

import maintenance
import alert_logger
import geo_zones
import forensics

# ─── Config ─────────────────────────────────────────────────────────
MODEL_PATH = "models/anomaly_model.pkl"
THRESHOLD = -0.05

# COCO class IDs for tool / equipment detection
TOOL_CLASSES = {
    24: "backpack",
    26: "handbag",
    28: "suitcase",
    43: "knife",
    76: "scissors",
}


# ─── Anomaly Detector (Vibration) ───────────────────────────────────
class AnomalyDetector:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            return joblib.load(MODEL_PATH)
        return None

    def predict(self, vibration_value):
        if vibration_value > 0.4:
            return -0.99, "CRITICAL"

        if self.model:
            input_vector = np.array([vibration_value, 0, 0]).reshape(1, -1)
            try:
                score = self.model.decision_function(input_vector)[0]
                status = "CRITICAL" if score < THRESHOLD else "STABLE"
                return score, status
            except Exception:
                return 0.0, "ERROR"
        else:
            status = "CRITICAL" if vibration_value > 0.35 else "STABLE"
            return 0.0, status


detector = AnomalyDetector()


# ─── Audio Extraction (Forensic Mode) ───────────────────────────────
def extract_audio_intensity(video_path, fps=30):
    try:
        clip = VideoFileClip(video_path)
        audio = clip.audio
        duration = clip.duration
        total_frames = int(duration * fps)
        intensities = []
        for t in np.linspace(0, duration, total_frames):
            chunk = audio.subclip(max(0, t - 0.05), min(duration, t + 0.05))
            rms = chunk.to_soundarray(fps=22000)
            if rms is not None and len(rms) > 0:
                volume = np.sqrt(np.mean(rms ** 2))
                intensities.append(volume)
            else:
                intensities.append(0.0)

        intensities = np.array(intensities)
        if np.max(intensities) > 0:
            intensities = intensities / np.max(intensities)
        return intensities
    except Exception as e:
        print(f"Audio Error: {e}")
        return []


# ─── YOLOv8 Vision ──────────────────────────────────────────────────
model_yolo = None


def load_yolo():
    global model_yolo
    if model_yolo is None:
        model_yolo = YOLO('yolov8n.pt')
    return model_yolo


# ─── Risk Score Calculator ──────────────────────────────────────────
def _compute_risk_score(person_detected, tool_detected, vibration_val,
                        vibration_status, is_under_maintenance, max_conf,
                        zone_bonus=0):
    """
    Compute a 0-100 numerical risk score using weighted factors.
    Higher = more dangerous. Includes geo-zone risk amplification.
    """
    score = 0.0

    # Base vibration contribution (0-40 points)
    if vibration_status == "CRITICAL":
        score += min(40, vibration_val * 80)
    else:
        score += min(10, vibration_val * 20)

    # Person detection (0-25 points)
    if person_detected:
        score += 15 + (max_conf * 10)  # higher confidence = higher risk

    # Tool detection (0-20 points)
    if tool_detected:
        score += 20

    # Combined person + vibration (multiplicative bonus)
    if person_detected and vibration_status == "CRITICAL":
        score += 15

    # Geo-zone risk amplification (0-20 points)
    score += zone_bonus

    # Maintenance suppression
    if is_under_maintenance:
        score = max(0, score * 0.15)  # Slash risk by 85% during maintenance

    return round(min(100, max(0, score)), 1)


def _severity_from_score(score):
    """Map numerical score to severity label."""
    if score >= 70:
        return "CRITICAL"
    elif score >= 45:
        return "WARNING"
    elif score >= 25:
        return "CAUTION"
    elif score >= 10:
        return "INFO"
    return "SAFE"


# ─── Main Threat Detection Pipeline ────────────────────────────────
def detect_threats(frame, vibration_val):
    """
    Run the full detection pipeline on a single frame.

    Returns:
        annotated_frame, alert_status, color, explanation, risk_score, max_confidence
    """
    # 1. Vibration anomaly score
    risk_score_raw, vibration_status = detector.predict(vibration_val)

    # 2. YOLOv8 object detection
    yolo = load_yolo()
    results = yolo(frame, verbose=False)
    result = results[0]
    annotated_frame = result.plot()

    person_detected = False
    tool_detected = False
    max_confidence = 0.0
    detected_objects = []

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        max_confidence = max(max_confidence, conf)

        if cls_id == 0:
            person_detected = True
            detected_objects.append(f"person ({conf:.0%})")
        elif cls_id in TOOL_CLASSES:
            tool_detected = True
            detected_objects.append(f"{TOOL_CLASSES[cls_id]} ({conf:.0%})")

    # 3. Maintenance check
    is_under_maintenance, maint_task = maintenance.get_maintenance_status("section_1")

    # 4. Geo-zone risk bonus
    zone_bonus = geo_zones.get_zone_risk_bonus()
    current_zone = geo_zones.get_current_zone()
    zone_name = current_zone.get("name", "Unknown")

    # 5. Compute numerical risk score (with zone amplification)
    risk_score = _compute_risk_score(
        person_detected, tool_detected, vibration_val,
        vibration_status, is_under_maintenance, max_confidence,
        zone_bonus=zone_bonus
    )
    severity = _severity_from_score(risk_score)

    # 6. Classification logic
    final_alert = "NORMAL"
    color = "green"
    explanation = "System Secure. No threats detected."
    det_str = ", ".join(detected_objects) if detected_objects else "none"
    zone_tag = f" | Zone: {zone_name}" if zone_bonus > 0 else ""

    if is_under_maintenance:
        final_alert = "✅ MAINTENANCE IN PROGRESS"
        color = "blue"
        if person_detected:
            explanation = (f"Person detected — flagged as AUTHORIZED WORKER.\n"
                           f"Task: {maint_task}\n"
                           f"Detections: {det_str}")
        elif vibration_status == "CRITICAL":
            explanation = (f"High vibration ({vibration_val:.2f}) — flagged as AUTHORIZED WORK.\n"
                           f"Task: {maint_task}")
        else:
            explanation = f"Scheduled Maintenance Active.\nTask: {maint_task}"

    elif person_detected and vibration_status == "CRITICAL":
        final_alert = "🚨 SABOTAGE DETECTED"
        color = "red"
        explanation = (f"CRITICAL: Unauthorized person + high vibration ({vibration_val:.2f})\n"
                       f"Detections: {det_str} | Risk: {risk_score}/100{zone_tag}")

    elif person_detected and tool_detected:
        final_alert = "⚠️ SUSPICIOUS ACTIVITY"
        color = "orange"
        explanation = (f"Person with equipment/tools detected.\n"
                       f"Detections: {det_str} | Risk: {risk_score}/100{zone_tag}")

    elif person_detected:
        final_alert = "⚠️ TRESPASSING"
        color = "orange"
        explanation = (f"Unauthorized person on track.\n"
                       f"Detections: {det_str} | Risk: {risk_score}/100{zone_tag}")

    elif tool_detected:
        final_alert = "🔍 ABANDONED EQUIPMENT"
        color = "yellow"
        explanation = (f"Equipment detected without personnel.\n"
                       f"Detections: {det_str} | Risk: {risk_score}/100{zone_tag}")

    elif vibration_status == "CRITICAL":
        final_alert = "🔧 MECHANICAL FAULT"
        color = "yellow"
        explanation = (f"Unexplained high vibration ({vibration_val:.2f}). No work scheduled.\n"
                       f"Risk: {risk_score}/100{zone_tag}")

    # 7. Log the alert (skip NORMAL to avoid flooding)
    if final_alert != "NORMAL":
        alert_logger.log_alert(
            alert_type=final_alert,
            severity=severity,
            risk_score=risk_score,
            vibration_level=vibration_val,
            detections=det_str,
            explanation=explanation,
        )

    # 8. Auto-generate forensic evidence for WARNING+ severity
    if severity in ("CRITICAL", "WARNING"):
        try:
            forensics.generate_incident_report(
                alert_type=final_alert, severity=severity,
                risk_score=risk_score, vibration_level=vibration_val,
                detections=det_str, explanation=explanation,
                frame=frame, zone=zone_name,
            )
        except Exception:
            pass  # Non-critical

    return annotated_frame, final_alert, color, explanation, risk_score, max_confidence


# ─── Phyphox Real-Time Sensor ───────────────────────────────────────
phyphox_url = ""


def set_phyphox_url(url):
    global phyphox_url
    if url and not url.startswith("http"):
        phyphox_url = f"http://{url}"
    else:
        phyphox_url = url


def get_real_vibration():
    global phyphox_url
    if not phyphox_url:
        return 0.0
    try:
        response = requests.get(
            f"{phyphox_url}/get?accX&accY&accZ", timeout=0.5
        )
        data = response.json()
        ax = data["buffer"]["accX"]["buffer"][-1]
        ay = data["buffer"]["accY"]["buffer"][-1]
        az = data["buffer"]["accZ"]["buffer"][-1]
        magnitude = np.sqrt(ax ** 2 + ay ** 2 + az ** 2)
        return abs(magnitude - 9.81) / 3.0
    except Exception:
        return 0.0