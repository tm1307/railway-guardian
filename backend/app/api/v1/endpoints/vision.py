from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Depends
from ....services.vision import vision_service
from ....core.security import get_current_user
import cv2
import numpy as np
import base64
import tempfile
import os
import logging

router = APIRouter()

@router.post("/analyze-video")
async def analyze_uploaded_video(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Upload a video file and run YOLOv8 detection on sampled frames."""
    if not file.filename:
        return {"error": "No file uploaded"}

    # Save uploaded video
    suffix = os.path.splitext(file.filename)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            return {"error": "Cannot open video file"}

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        duration = total_frames / fps if fps > 0 else 0

        # Sample up to 10 frames evenly across the video
        num_samples = min(10, max(3, total_frames // 30))
        sample_indices = [int(i * total_frames / num_samples) for i in range(num_samples)]

        all_results = []
        frame_detections = {}

        for idx in sample_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue

            timestamp_sec = round(idx / fps, 2)
            detections = vision_service.process_frame(frame)

            frame_result = {
                "frame_index": idx,
                "timestamp_sec": timestamp_sec,
                "timestamp_display": f"{int(timestamp_sec // 60):02d}:{int(timestamp_sec % 60):02d}",
                "detections": detections,
                "detection_count": len(detections),
            }
            all_results.append(frame_result)

            # Track detection counts by class
            for d in detections:
                cls = d.get("class", "unknown")
                frame_detections[cls] = frame_detections.get(cls, 0) + 1

        cap.release()

        # ─── MoviePy Audio Analysis ──────────────────────────────
        audio_analysis = {"has_audio": False, "avg_volume_db": 0, "peak_volume_db": 0, "anomaly_count": 0, "anomalies": []}
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(tmp_path)
            if clip.audio is not None:
                audio_analysis["has_audio"] = True
                # Sample audio at 22050 Hz
                audio_arr = clip.audio.to_soundarray(fps=22050)
                if len(audio_arr) > 0:
                    # RMS volume per chunk (0.5 second windows)
                    chunk_size = 22050 // 2  # 0.5s chunks
                    volumes = []
                    for i in range(0, len(audio_arr) - chunk_size, chunk_size):
                        chunk = audio_arr[i:i + chunk_size]
                        rms = float(np.sqrt(np.mean(chunk ** 2)))
                        volumes.append(rms)

                    if volumes:
                        import math
                        avg_rms = sum(volumes) / len(volumes)
                        peak_rms = max(volumes)
                        # Convert to dB (rough approximation)
                        avg_db = round(20 * math.log10(max(avg_rms, 1e-10)), 1)
                        peak_db = round(20 * math.log10(max(peak_rms, 1e-10)), 1)
                        audio_analysis["avg_volume_db"] = avg_db
                        audio_analysis["peak_volume_db"] = peak_db

                        # Detect anomalies: sudden volume spikes > 3x average
                        threshold = avg_rms * 3 if avg_rms > 0 else 0.1
                        anomalies = []
                        for i, vol in enumerate(volumes):
                            if vol > threshold:
                                timestamp = round(i * 0.5, 1)
                                spike_db = round(20 * math.log10(max(vol, 1e-10)), 1)
                                anomalies.append({
                                    "timestamp": timestamp,
                                    "volume_db": spike_db,
                                    "type": "impact_sound" if spike_db > -10 else "loud_event",
                                    "description": f"Volume spike to {spike_db}dB (avg: {avg_db}dB) — possible tampering/impact sound"
                                })
                        audio_analysis["anomaly_count"] = len(anomalies)
                        audio_analysis["anomalies"] = anomalies[:10]  # Top 10
            clip.close()
        except ImportError:
            audio_analysis["error"] = "moviepy not installed — run: pip install moviepy"
            logging.warning("moviepy not installed, skipping audio analysis")
        except Exception as e:
            audio_analysis["error"] = str(e)
            logging.warning(f"Audio analysis error: {e}")

        # Summary analysis
        total_detections = sum(r["detection_count"] for r in all_results)
        threat_objects = {k: v for k, v in frame_detections.items() if k not in ("person",)}
        has_threats = len(threat_objects) > 0 or audio_analysis.get("anomaly_count", 0) > 2

        return {
            "filename": file.filename,
            "duration_sec": round(duration, 1),
            "total_frames": total_frames,
            "frames_analyzed": len(all_results),
            "total_detections": total_detections,
            "detection_summary": frame_detections,
            "threat_detected": has_threats,
            "threat_objects": threat_objects,
            "risk_level": "HIGH" if has_threats and total_detections > 5 else "MEDIUM" if total_detections > 2 else "LOW",
            "frame_results": all_results,
            "audio_analysis": audio_analysis,
        }

    finally:
        os.unlink(tmp_path)


@router.websocket("/ws/vision-stream")
async def websocket_vision_endpoint(websocket: WebSocket):
    """WebSocket for live webcam YOLOv8 detection."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if not data:
                continue

            try:
                # Remove data URI prefix
                if "," in data:
                    data = data.split(",")[1]

                img_bytes = base64.b64decode(data)
                np_arr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is not None:
                    detections = vision_service.process_frame(frame)
                    formatted = [{
                        "label": d["class"],
                        "confidence": d["confidence"],
                        "box": [float(x) for x in d["box"]],
                    } for d in detections]
                    await websocket.send_json({"detections": formatted})
                else:
                    await websocket.send_json({"error": "Failed to decode frame"})
            except Exception as e:
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        logging.info("Vision client disconnected")
    except Exception as e:
        logging.error(f"Vision WS error: {e}")
        try:
            await websocket.close()
        except:
            pass
