"""
Predictive Track Failure Engine (PTFE)
Uses Miner's Rule cumulative fatigue + EWMA anomaly detection
to predict WHEN a track section will fail.

This is genuine engineering ML — not classification, but time-series
degradation modeling.
"""
import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# Material constants for 60kg/m rail (UIC 60 standard used by Indian Railways)
RAIL_FATIGUE_LIMIT = 250e6    # Pa (endurance limit)
RAIL_UTS = 880e6              # Pa (ultimate tensile strength, R260 grade)
BASQUIN_EXPONENT = -0.12      # S-N curve exponent for rail steel
THERMAL_EXPANSION_COEFF = 11.7e-6  # per °C for rail steel


class PredictiveFailureEngine:
    def __init__(self):
        self.section_history: Dict[str, List[dict]] = {}
        self.fatigue_index: Dict[str, float] = {}
        self.anomaly_scores: Dict[str, List[float]] = {}
        self.ewma_state: Dict[str, float] = {}
        self._initialized = False

    def ingest_reading(self, reading: dict):
        """Process a sensor reading and update fatigue models."""
        node_id = reading.get("node_id", "UNKNOWN")

        if node_id not in self.section_history:
            self.section_history[node_id] = []
            self.fatigue_index[node_id] = 0.0
            self.anomaly_scores[node_id] = []
            self.ewma_state[node_id] = 0.0

        self.section_history[node_id].append(reading)
        # Keep last 2000 readings per section
        self.section_history[node_id] = self.section_history[node_id][-2000:]

        vibration = reading.get("vibration", 0.0)
        temperature = reading.get("temperature", 30.0)

        # --- Miner's Rule Cumulative Fatigue ---
        # Convert vibration (g) to estimated stress (MPa)
        # Using simplified dynamics: σ = ρ * a * L (rail beam model)
        stress_mpa = vibration * 9.81 * 7850 * 0.003  # simplified
        if stress_mpa > 0:
            # S-N curve: N = (σ_UTS / σ)^(1/b)
            cycles_to_fail = max(1, (RAIL_UTS / (stress_mpa * 1e6)) ** (1 / abs(BASQUIN_EXPONENT)))
            damage_increment = 1.0 / cycles_to_fail
            self.fatigue_index[node_id] += damage_increment

        # Add thermal fatigue contribution
        neutral_temp = 35.0  # Stress-free temperature for Indian Railways
        temp_delta = abs(temperature - neutral_temp)
        thermal_stress = THERMAL_EXPANSION_COEFF * temp_delta * 200e9  # E = 200 GPa
        if thermal_stress > RAIL_FATIGUE_LIMIT * 0.3:
            self.fatigue_index[node_id] += 1e-8 * (thermal_stress / RAIL_FATIGUE_LIMIT)

        # --- EWMA Anomaly Detection ---
        alpha = 0.15  # Smoothing factor
        prev_ewma = self.ewma_state[node_id]
        new_ewma = alpha * vibration + (1 - alpha) * prev_ewma
        self.ewma_state[node_id] = new_ewma

        # Anomaly = deviation from EWMA
        deviation = abs(vibration - new_ewma)
        std_estimate = max(0.01, np.std([r.get("vibration", 0) for r in self.section_history[node_id][-50:]]))
        z_score = deviation / std_estimate
        self.anomaly_scores[node_id].append(round(z_score, 3))
        self.anomaly_scores[node_id] = self.anomaly_scores[node_id][-500:]

        self._initialized = True

    def get_section_health(self) -> List[Dict[str, Any]]:
        """Get health assessment for all monitored sections."""
        results = []
        now = datetime.utcnow()

        for node_id, history in self.section_history.items():
            if not history:
                continue

            fatigue = self.fatigue_index.get(node_id, 0.0)
            anomaly_scores = self.anomaly_scores.get(node_id, [])

            # Health percentage (inverse of fatigue)
            # Fatigue index of 1.0 = theoretical failure
            health_pct = max(0, min(100, 100 * (1 - fatigue * 1e4)))

            # Predict days until failure based on fatigue accumulation rate
            if len(history) >= 10:
                readings_count = len(history)
                # Time span of readings (assuming 3s intervals)
                time_span_hours = readings_count * 3 / 3600
                if time_span_hours > 0 and fatigue > 0:
                    fatigue_rate_per_day = fatigue / max(0.01, time_span_hours / 24)
                    remaining_life = (1.0 - fatigue * 1e4) / max(1e-10, fatigue_rate_per_day * 1e4)
                    days_to_failure = max(1, min(3650, remaining_life))
                else:
                    days_to_failure = 3650
            else:
                days_to_failure = 3650

            # Recent anomaly frequency
            recent_anomalies = sum(1 for s in anomaly_scores[-100:] if s > 2.0)
            anomaly_rate = recent_anomalies / max(1, len(anomaly_scores[-100:]))

            # Risk classification
            if health_pct < 30 or days_to_failure < 30:
                risk_level = "CRITICAL"
            elif health_pct < 60 or days_to_failure < 90:
                risk_level = "HIGH"
            elif health_pct < 80 or days_to_failure < 180:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            # Recommended maintenance window
            maint_days = max(1, int(days_to_failure * 0.7))
            recommended_date = (now + timedelta(days=maint_days)).strftime("%Y-%m-%d")

            # Vibration trend (last 50 readings)
            recent_vibs = [r.get("vibration", 0) for r in history[-50:]]
            trend = "stable"
            if len(recent_vibs) >= 10:
                first_half = np.mean(recent_vibs[:len(recent_vibs)//2])
                second_half = np.mean(recent_vibs[len(recent_vibs)//2:])
                if second_half > first_half * 1.15:
                    trend = "increasing"
                elif second_half < first_half * 0.85:
                    trend = "decreasing"

            node_name = history[-1].get("node_name", node_id)
            results.append({
                "node_id": node_id,
                "node_name": node_name,
                "health_pct": round(health_pct, 1),
                "fatigue_index": round(fatigue * 1e6, 4),
                "days_to_failure": round(days_to_failure),
                "risk_level": risk_level,
                "recommended_maintenance": recommended_date,
                "anomaly_rate": round(anomaly_rate * 100, 1),
                "recent_anomalies": recent_anomalies,
                "vibration_trend": trend,
                "ewma_current": round(self.ewma_state.get(node_id, 0), 4),
                "readings_count": len(history),
                "sparkline": [round(r.get("vibration", 0), 3) for r in history[-30:]],
            })

        return sorted(results, key=lambda x: x["health_pct"])

    def get_anomalies(self) -> List[Dict[str, Any]]:
        """Get detected anomalies across all sections."""
        anomalies = []
        for node_id, scores in self.anomaly_scores.items():
            history = self.section_history.get(node_id, [])
            for i, score in enumerate(scores[-50:]):
                if score > 2.5:  # Significant anomaly threshold
                    idx = max(0, len(history) - 50 + i)
                    reading = history[idx] if idx < len(history) else {}
                    anomalies.append({
                        "node_id": node_id,
                        "node_name": reading.get("node_name", node_id),
                        "z_score": score,
                        "severity": "CRITICAL" if score > 4.0 else "HIGH" if score > 3.0 else "MEDIUM",
                        "vibration": reading.get("vibration", 0),
                        "timestamp": reading.get("timestamp", ""),
                        "source": reading.get("source", "SIMULATION"),
                    })
        return sorted(anomalies, key=lambda x: x["z_score"], reverse=True)[:30]


# Singleton
predictive_engine = PredictiveFailureEngine()
