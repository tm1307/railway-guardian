"""
Real ML Intent Prediction Engine
Uses sklearn trained models to predict threat types and confidence from multi-sensor features.
"""
import numpy as np
import math
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

logger = logging.getLogger(__name__)
MODEL_PATH = "data/models"

THREAT_TYPES = ["safe", "tampering", "theft", "vandalism", "trespassing"]

ZONES = [
    "New Delhi Railway Station", "Old Delhi Junction", "Hazrat Nizamuddin",
    "Anand Vihar Terminal", "Ghaziabad Junction", "Sarai Rohilla",
    "Tilak Bridge Section", "Okhla Railway Crossing", "Shakurbasti Yard",
    "Faridabad Section", "Tughlakabad Depot", "Subzi Mandi Area",
]

class IntentPredictionEngine:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(THREAT_TYPES)
        self._train_model()

    def _generate_training_data(self):
        """Generate training set based on known threat patterns."""
        np.random.seed(123)
        X, y = [], []

        for _ in range(3000):
            hour = np.random.randint(0, 24)
            is_night = 1 if (hour >= 22 or hour <= 5) else 0
            vibration = np.random.exponential(0.12) + 0.02
            temperature = 25 + 10 * np.sin((hour - 6) * np.pi / 12) + np.random.normal(0, 2)
            acoustic = 25 + np.random.exponential(15)
            strain = np.random.exponential(30) + 10
            person_detected = np.random.binomial(1, 0.3 if is_night else 0.1)
            object_detected = np.random.binomial(1, 0.15)
            maintenance_active = np.random.binomial(1, 0.2)
            recent_alerts = np.random.poisson(1)

            features = [hour, is_night, vibration, temperature, acoustic, strain,
                       person_detected, object_detected, maintenance_active, recent_alerts]

            # Label assignment based on patterns
            if maintenance_active and person_detected:
                label = "safe"
            elif vibration > 0.4 and person_detected and not maintenance_active:
                label = np.random.choice(["tampering", "theft"], p=[0.6, 0.4])
            elif person_detected and is_night and not maintenance_active:
                label = np.random.choice(["trespassing", "theft"], p=[0.7, 0.3])
            elif object_detected and vibration > 0.3:
                label = np.random.choice(["vandalism", "tampering"], p=[0.5, 0.5])
            elif vibration > 0.5:
                label = np.random.choice(["tampering", "vandalism"], p=[0.7, 0.3])
            else:
                label = "safe"

            X.append(features)
            y.append(label)

        return np.array(X), np.array(y)

    def _train_model(self):
        """Train the intent prediction classifier."""
        try:
            X, y = self._generate_training_data()
            X_scaled = self.scaler.fit_transform(X)
            y_encoded = self.label_encoder.transform(y)

            self.model = RandomForestClassifier(
                n_estimators=150, max_depth=12, random_state=42,
                class_weight="balanced", n_jobs=-1
            )
            self.model.fit(X_scaled, y_encoded)

            os.makedirs(MODEL_PATH, exist_ok=True)
            joblib.dump(self.model, f"{MODEL_PATH}/intent_classifier.pkl")
            joblib.dump(self.scaler, f"{MODEL_PATH}/intent_scaler.pkl")

            logger.info("ML Intent model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train intent model: {e}")

    def predict_single(self, zone_name: str, sensor_data: dict = None, maintenance_active: bool = False):
        """Predict intent for a single zone."""
        now = datetime.utcnow()
        hour = now.hour
        is_night = 1 if (hour >= 22 or hour <= 5) else 0

        sd = sensor_data or {}
        features = np.array([[
            hour, is_night,
            sd.get("vibration", 0.08),
            sd.get("temperature", 30),
            sd.get("acoustic", 30),
            sd.get("strain", 40),
            sd.get("person_detected", 0),
            sd.get("object_detected", 0),
            1 if maintenance_active else 0,
            sd.get("recent_alerts", 0),
        ]])

        if self.model:
            features_scaled = self.scaler.transform(features)
            pred_idx = self.model.predict(features_scaled)[0]
            probas = self.model.predict_proba(features_scaled)[0]
            predicted = self.label_encoder.inverse_transform([pred_idx])[0]
            confidence = float(max(probas))

            # Get top 2 threats with probabilities
            sorted_indices = np.argsort(probas)[::-1]
            top_threats = [(self.label_encoder.inverse_transform([i])[0], float(probas[i]))
                          for i in sorted_indices[:3]]
        else:
            predicted = "safe"
            confidence = 0.5
            top_threats = [("safe", 0.5)]

        # Generate reasoning
        reasoning_parts = []
        if is_night: reasoning_parts.append("Night-time operations")
        if sd.get("vibration", 0) > 0.3: reasoning_parts.append(f"High vibration ({sd.get('vibration', 0):.3f}g)")
        if maintenance_active: reasoning_parts.append("Maintenance window active")
        if sd.get("person_detected"): reasoning_parts.append("Person detected on track")
        reasoning = ". ".join(reasoning_parts) if reasoning_parts else "Normal operating conditions"

        actions = {
            "tampering": "Deploy RPF patrol immediately. Secure track section.",
            "theft": "Alert control room. Dispatch nearest responder.",
            "vandalism": "Increase surveillance. Document evidence.",
            "trespassing": "Issue warning. Monitor movement pattern.",
            "safe": "Continue standard monitoring.",
        }

        return {
            "zone_name": zone_name,
            "predicted_threat": predicted,
            "confidence": round(confidence, 3),
            "top_threats": top_threats,
            "reasoning": reasoning,
            "recommended_action": actions.get(predicted, "Monitor"),
            "time_window": f"{now.strftime('%H:%M')} - {(now + timedelta(hours=1)).strftime('%H:%M')}",
            "model": "RandomForest (n=150, balanced)",
            "maintenance_suppressed": maintenance_active and predicted == "safe",
        }

    def get_predictions(self, sensor_data: dict = None, active_maintenance_zones: list = None):
        """Get predictions for all zones."""
        am = active_maintenance_zones or []
        return [self.predict_single(z, sensor_data, z in am) for z in ZONES]

    def get_timeline(self, sensor_data: dict = None):
        """Get 24-hour threat prediction timeline."""
        now = datetime.utcnow()
        timeline = []
        for i in range(24):
            h = (now.hour + i) % 24
            is_night = 1 if (h >= 22 or h <= 5) else 0

            features = np.array([[
                h, is_night, 0.1, 30, 30, 40, 0, 0, 0, 0
            ]])

            if self.model:
                features_scaled = self.scaler.transform(features)
                probas = self.model.predict_proba(features_scaled)[0]
                safe_idx = list(self.label_encoder.classes_).index("safe")
                threat_prob = 1 - probas[safe_idx]
            else:
                threat_prob = 0.3 + is_night * 0.3

            timeline.append({
                "hour": f"{h:02d}:00",
                "threat_count": round(threat_prob * 10, 1),
                "safe_count": round((1 - threat_prob) * 10, 1),
                "threat_probability": round(threat_prob, 3),
            })
        return timeline


intent_service = IntentPredictionEngine()
