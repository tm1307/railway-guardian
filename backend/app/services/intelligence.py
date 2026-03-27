import numpy as np
import cv2
import os
import joblib
from ultralytics import YOLO
from typing import Tuple, Dict, Any, List
from collections import deque
import datetime

# ─── Config ─────────────────────────────────────────────────────────
MODEL_PATH = "models/anomaly_model.pkl"
VIBRATION_THRESHOLD = 0.35
WINDOW_SIZE = 40
ESCALATION_SLOPE = 0.003

TOOL_CLASSES = {
    24: "backpack",
    26: "handbag",
    28: "suitcase",
    43: "knife",
    76: "scissors",
}

class NightVisionProcessor:
    def __init__(self):
        self._clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

    def process(self, frame: np.ndarray) -> Tuple[np.ndarray, bool, float, str]:
        if frame is None: return frame, False, 100, "UNKNOWN"
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        brightness = float(np.mean(hsv[:, :, 2]))
        is_night = brightness < 90
        label = "NIGHT" if brightness < 60 else ("DUSK" if brightness < 90 else "DAY")
        
        if is_night:
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l = self._clahe.apply(l)
            frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
            
        return frame, is_night, brightness, label

class IntelligenceService:
    def __init__(self):
        self.yolo = None
        self._loaded_yolo = False
        self.night_processor = NightVisionProcessor()
        self.vibration_window = deque(maxlen=WINDOW_SIZE)
        self.anomaly_model = self._load_model()
        
    def _ensure_yolo(self):
        if not self._loaded_yolo:
            self.yolo = YOLO('yolov8n.pt')
            self._loaded_yolo = True

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            return joblib.load(MODEL_PATH)
        return None

    def analyze_vibration(self, value: float) -> Tuple[str, float]:
        self.vibration_window.append(value)
        status = "CRITICAL" if value > VIBRATION_THRESHOLD else "STABLE"
        
        # Simple trend analysis
        if len(self.vibration_window) > 5:
            y = np.array(self.vibration_window)
            x = np.arange(len(y))
            slope = np.polyfit(x, y, 1)[0]
            if slope > ESCALATION_SLOPE:
                status = "ESCALATING"
        
        return status, value

    def detect_objects(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        self._ensure_yolo()
        results = self.yolo(frame, verbose=False)
        result = results[0]
        detections = []
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if cls_id == 0 or cls_id in TOOL_CLASSES:
                detections.append({
                    "class": "person" if cls_id == 0 else TOOL_CLASSES[cls_id],
                    "confidence": conf,
                    "box": box.xyxy[0].tolist()
                })
        return result.plot(), detections

    def compute_risk_score(self, detections: List[Dict], vibration_val: float, vibration_status: str, is_night: bool) -> float:
        score = 0.0
        person_detected = any(d["class"] == "person" for d in detections)
        tool_detected = any(d["class"] != "person" for d in detections)
        
        if vibration_status == "CRITICAL": score += 40
        if person_detected: score += 25
        if tool_detected: score += 15
        if is_night and person_detected: score += 10
        if person_detected and vibration_status == "CRITICAL": score += 10
        
        return min(100.0, score)

    async def process_frame(self, frame: np.ndarray, vibration_val: float) -> Dict[str, Any]:
        # 1. Night Vision
        processed_frame, is_night, brightness, light_label = self.night_processor.process(frame)
        
        # 2. Vibration Analysis
        vib_status, vib_val = self.analyze_vibration(vibration_val)
        
        # 3. Object Detection
        annotated_frame, detections = self.detect_objects(processed_frame)
        
        # 4. Risk Scoring
        risk_score = self.compute_risk_score(detections, vib_val, vib_status, is_night)
        
        return {
            "risk_score": risk_score,
            "vibration_status": vib_status,
            "vibration_value": vib_val,
            "detections": detections,
            "is_night": is_night,
            "light_label": light_label,
            "timestamp": datetime.datetime.now().isoformat()
        }

intelligence_service = IntelligenceService()
