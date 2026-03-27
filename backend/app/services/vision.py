from ultralytics import YOLO
import cv2
import os
import numpy as np
import logging

# Detect ALL COCO classes, not just a small subset
SECURITY_CLASSES = {
    0: "person", 24: "backpack", 25: "umbrella", 26: "handbag", 28: "suitcase",
    39: "bottle", 41: "cup", 43: "knife", 44: "spoon", 56: "chair",
    63: "laptop", 64: "mouse", 66: "keyboard", 67: "cell phone",
    73: "book", 76: "scissors",
}

class VisionService:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = None
        self.model_path = model_path
        self._loaded = False

    def _ensure_model(self):
        """Lazy load the PyTorch model into memory only when first requested.
        This prevents Render Free Tier OOM crashes when 4 Gunicorn workers start simultaneously.
        """
        if not self._loaded:
            try:
                self.model = YOLO(self.model_path)
                logging.info(f"YOLOv8 model loaded dynamically from {self.model_path}")
                self._loaded = True
            except Exception as e:
                logging.error(f"Failed to load YOLOv8 model: {e}")
                self._loaded = False

    def process_frame(self, frame: np.ndarray):
        """Run YOLOv8 on a raw numpy frame (from webcam). Returns list of detections."""
        self._ensure_model()
        if self.model is None or frame is None:
            return []

        results = self.model(frame, verbose=False, conf=0.3)
        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = self.model.names.get(cls_id, f"class_{cls_id}")

                # Detect all objects for a visible demo, not just security-specific
                detections.append({
                    "class": label,
                    "confidence": conf,
                    "box": box.xyxy[0].tolist(),
                })

        return detections

    def detect_threats(self, image_path: str):
        """Run YOLOv8 on an image file path. Returns (detections, max_conf)."""
        self._ensure_model()
        if not self.model or not os.path.exists(image_path):
            return [], 0.0

        results = self.model(image_path, verbose=False)
        detections = []
        max_conf = 0.0

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = self.model.names[cls]

                detections.append({
                    "label": label,
                    "confidence": conf,
                    "box": [float(x) for x in box.xyxy[0]]
                })
                if conf > max_conf:
                    max_conf = conf

        return detections, max_conf

vision_service = VisionService()
