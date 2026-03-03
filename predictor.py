"""
AI-Powered Predictive Intelligence — Innovation in proactive railway security.
Uses sliding-window trend analysis with linear regression to detect
escalating vibration patterns BEFORE they become critical incidents.

Innovation Highlights:
  - Shifts railway security from REACTIVE to PREDICTIVE
  - Estimates time-to-breach for critical thresholds
  - Enables preemptive dispatch of railway protection force
  - Reduces response time from minutes to advance warning
  - Can be extended with LSTM/transformer models for deeper prediction

This moves beyond traditional detection (what IS happening) to
prediction (what WILL happen) — a key differentiator for smart
railway governance under Digital India / Kavach initiatives.
"""

import numpy as np
from collections import deque

# ─── Config ─────────────────────────────────────────────────────────
WINDOW_SIZE = 40          # Number of recent readings to analyze
CRITICAL_THRESHOLD = 0.35  # Vibration level considered critical
ESCALATION_SLOPE = 0.003   # Slope threshold to flag escalation


class PredictiveEngine:
    """
    Sliding-window predictive analysis for vibration trends.
    Uses real-time linear regression to detect ESCALATING patterns
    and estimate time-to-breach, enabling preemptive action.
    """

    def __init__(self, window_size=WINDOW_SIZE):
        self.window = deque(maxlen=window_size)
        self.window_size = window_size

    def update(self, vibration_value):
        """Add a new vibration reading to the sliding window."""
        self.window.append(float(vibration_value))

    def get_trend(self):
        """
        Compute the trend slope using linear regression.
        Returns: (slope, r_squared)
        """
        if len(self.window) < 5:
            return 0.0, 0.0

        y = np.array(self.window)
        x = np.arange(len(y))

        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x ** 2)

        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return 0.0, 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n

        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return round(slope, 6), round(max(0, r_squared), 4)

    def get_prediction(self):
        """
        Predict the vibration trend status.
        Returns: dict with status, confidence, slope, and actionable description.
        """
        slope, r_squared = self.get_trend()
        confidence = min(1.0, abs(r_squared))

        if len(self.window) < 5:
            return {
                "status": "CALIBRATING",
                "icon": "⏳",
                "color": "#6b7b8d",
                "slope": 0.0,
                "confidence": 0.0,
                "description": f"Collecting sensor data... ({len(self.window)}/{self.window_size})",
            }

        if slope > ESCALATION_SLOPE and r_squared > 0.15:
            return {
                "status": "ESCALATING",
                "icon": "🔺",
                "color": "#ef4444",
                "slope": slope,
                "confidence": confidence,
                "description": f"⚠️ Vibration rising — preemptive alert recommended",
            }
        elif slope < -ESCALATION_SLOPE and r_squared > 0.15:
            return {
                "status": "DE-ESCALATING",
                "icon": "🔻",
                "color": "#22c55e",
                "slope": slope,
                "confidence": confidence,
                "description": f"Vibration declining — threat subsiding",
            }
        else:
            return {
                "status": "STABLE",
                "icon": "➡️",
                "color": "#3b82f6",
                "slope": slope,
                "confidence": confidence,
                "description": "No significant trend — monitoring continues",
            }

    def get_estimated_time_to_critical(self):
        """
        If vibration is escalating, estimate how many readings until
        the critical threshold is breached. Enables preemptive dispatch
        of Railway Protection Force (RPF).
        Returns: int (readings to breach) or None if not escalating.
        """
        if len(self.window) < 5:
            return None

        slope, r_squared = self.get_trend()
        current_level = np.mean(list(self.window)[-5:])

        if slope <= ESCALATION_SLOPE or r_squared < 0.15:
            return None

        if current_level >= CRITICAL_THRESHOLD:
            return 0

        remaining = CRITICAL_THRESHOLD - current_level
        if slope > 0:
            readings_to_critical = int(remaining / slope)
            return max(0, readings_to_critical)

        return None

    def get_current_stats(self):
        """Return summary statistics of the current window."""
        if len(self.window) < 2:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}

        data = np.array(self.window)
        return {
            "mean": round(float(np.mean(data)), 4),
            "std": round(float(np.std(data)), 4),
            "min": round(float(np.min(data)), 4),
            "max": round(float(np.max(data)), 4),
        }

    def reset(self):
        """Clear the sliding window."""
        self.window.clear()
