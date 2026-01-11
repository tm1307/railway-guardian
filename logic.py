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


MODEL_PATH = "models/anomaly_model.pkl"
THRESHOLD = -0.05
TOOL_CLASSES = [24, 26, 28, 43, 76]  

class AnomalyDetector:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            return joblib.load(MODEL_PATH)
        else:
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
            except:
                return 0.0, "ERROR"
        else:
            status = "CRITICAL" if vibration_value > 0.35 else "STABLE"
            return 0.0, status

detector = AnomalyDetector()


def extract_audio_intensity(video_path, fps=30):
    try:
        clip = VideoFileClip(video_path)
        audio = clip.audio
        duration = clip.duration
        total_frames = int(duration * fps)
        intensities = []
        for t in np.linspace(0, duration, total_frames):
            chunk = audio.subclip(max(0, t-0.05), min(duration, t+0.05))
            rms = chunk.to_soundarray(fps=22000)
            if rms is not None and len(rms) > 0:
                volume = np.sqrt(np.mean(rms**2))
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


model_yolo = None

def load_yolo():
    global model_yolo
    if model_yolo is None:
        model_yolo = YOLO('yolov8n.pt') 
    return model_yolo

def detect_threats(frame, vibration_val):
   
    risk_score, vibration_status = detector.predict(vibration_val)
    
    yolo = load_yolo()
    results = yolo(frame, verbose=False)
    result = results[0]
    annotated_frame = result.plot()
    
    person_detected = False
    tool_detected = False
    for box in result.boxes:
        cls_id = int(box.cls[0])
        if cls_id == 0: person_detected = True
        elif cls_id in TOOL_CLASSES: tool_detected = True
            
   
    is_under_maintenance, maint_task = maintenance.get_maintenance_status("section_1")

    
    final_alert = "NORMAL"
    color = "green"
    explanation = "System Secure."
    
    
    if is_under_maintenance:
        final_alert = "✅ MAINTENANCE IN PROGRESS"
        color = "blue"
        
        if person_detected:
            explanation = f"⚠️ Person detected, but flagged as AUTHORIZED WORKER.\nTask: {maint_task}"
        elif vibration_status == "CRITICAL":
            explanation = f"⚠️ High vibration detected, but flagged as AUTHORIZED WORK.\nTask: {maint_task}"
        else:
            explanation = f"Scheduled Maintenance Active.\nTask: {maint_task}"

    
    elif person_detected and vibration_status == "CRITICAL":
        final_alert = "🚨 SABOTAGE DETECTED"
        color = "red"
        explanation = f"CRITICAL: Unauthorized Person + High Impact ({vibration_val:.2f})"
        
    elif person_detected and tool_detected:
        final_alert = "⚠️ SUSPICIOUS ACTIVITY"
        color = "orange"
        explanation = "WARNING: Person detected carrying equipment/tools."

    elif person_detected:
        final_alert = "⚠️ TRESPASSING"
        color = "orange" 
        explanation = "WARNING: Unauthorized person on track."
        
    elif vibration_status == "CRITICAL":
        final_alert = "🔧 MECHANICAL FAULT"
        color = "yellow"
        explanation = f"ALERT: Unexplained high vibration ({vibration_val:.2f}). No work scheduled."

    return annotated_frame, final_alert, color, explanation


phyphox_url = ""
def set_phyphox_url(url):
    global phyphox_url
    if url and not url.startswith("http"): phyphox_url = f"http://{url}"
    else: phyphox_url = url

def get_real_vibration():
    global phyphox_url
    if not phyphox_url: return 0.0
    try:
        response = requests.get(f"{phyphox_url}/get?accX&accY&accZ", timeout=0.5)
        data = response.json()
        ax = data["buffer"]["accX"]["buffer"][-1]
        ay = data["buffer"]["accY"]["buffer"][-1]
        az = data["buffer"]["accZ"]["buffer"][-1]
        magnitude = np.sqrt(ax**2 + ay**2 + az**2)
        return abs(magnitude - 9.81) / 3.0 
    except:
        return 0.0