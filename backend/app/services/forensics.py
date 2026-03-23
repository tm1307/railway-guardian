import os
import logging
from .vision import vision_service

class ForensicsService:
    def __init__(self, upload_dir="data/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    async def process_video(self, video_path: str):
        """Extract frames using OpenCV and run vision detection."""
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return []
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            all_detections = []
            
            # Sample 3 frames: start, middle, end
            for idx in [0, total_frames // 2, max(0, total_frames - 2)]:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frame_path = f"{video_path}_frame_{idx}.jpg"
                    cv2.imwrite(frame_path, frame)
                    detections, _ = vision_service.detect_threats(frame_path)
                    all_detections.extend(detections)
                    os.remove(frame_path)
            
            cap.release()
            return all_detections
        except Exception as e:
            logging.error(f"Forensics Error: {e}")
            return []

forensics_service = ForensicsService()
