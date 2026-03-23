from typing import List, Optional
import logging

class FusionEngine:
    def __init__(self):
        # Weighting factors for dynamic scoring
        self.WEIGHT_VISION = 0.5
        self.WEIGHT_VIBRATION = 0.3
        self.WEIGHT_CONTEXT = 0.2

    async def classify_incident(self, 
                                vision_detections: List[dict], 
                                vibration_peak: float, 
                                is_maintenance_active: bool,
                                confidence_score: float = 1.0):
        
        # Base classification logic
        # 1. Trespassing: Vision detects person, no maintenance
        # 2. Maintenance: Vision detects person + tools, maintenance active
        # 3. Mechanical Fault: High vibration, no vision detection
        # 4. Sabotage/Theft: High vibration + suspicious vision (tools/bag), no maintenance
        
        has_person = any(d['label'] == 'person' for d in vision_detections)
        has_tools = any(d['label'] in ['tool', 'backpack', 'suitcase'] for d in vision_detections)
        
        # Vibration Thresholds
        VIB_THRESHOLD_HIGH = 3.5
        VIB_THRESHOLD_LOW = 0.5
        
        if is_maintenance_active:
            if has_person:
                return "MAINTENANCE", "Authorized personal on site for scheduled task."
            return "MAINTENANCE", "Scheduled maintenance activity detected."
            
        if vibration_peak > VIB_THRESHOLD_HIGH:
            if has_person or has_tools:
                return "SABOTAGE", f"Critical anomaly: Suspicious activity detected with high vibration ({vibration_peak}g)."
            return "MECHANICAL_FAULT", f"Structural anomaly detected: High vibration ({vibration_peak}g) without visual intrusion."
            
        if has_person:
            if has_tools:
                return "THEFT_ATTEMPT", "Alert: Potential theft or sabotage in progress. Tools detected."
            return "TRESPASSING", "Security alert: Unauthorized person on track."
            
        if vibration_peak > VIB_THRESHOLD_LOW:
            return "UNKNOWN_ANOMALY", f"Minor vibration detected ({vibration_peak}g). Monitoring initiated."
            
        return "NORMAL", "System status green. No significant threats detected."

fusion_engine = FusionEngine()
