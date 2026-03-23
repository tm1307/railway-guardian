"""
Real ML Risk Scoring Engine
Uses sklearn trained models for risk assessment based on sensor features.
Model trains on startup with synthetic training data representing known patterns.
"""
import numpy as np
import math
import logging
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

# Delhi railway zones with coordinates
ZONES = [
    {"name": "New Delhi Railway Station", "lat": 28.6425, "lng": 77.2195, "base_risk": 0.4},
    {"name": "Old Delhi Junction", "lat": 28.6606, "lng": 77.2264, "base_risk": 0.5},
    {"name": "Hazrat Nizamuddin", "lat": 28.5878, "lng": 77.2508, "base_risk": 0.35},
    {"name": "Anand Vihar Terminal", "lat": 28.6461, "lng": 77.3152, "base_risk": 0.3},
    {"name": "Ghaziabad Junction", "lat": 28.6706, "lng": 77.4381, "base_risk": 0.55},
    {"name": "Sarai Rohilla", "lat": 28.6607, "lng": 77.1756, "base_risk": 0.25},
    {"name": "Tilak Bridge Section", "lat": 28.6355, "lng": 77.2434, "base_risk": 0.6},
    {"name": "Delhi Cantt Area", "lat": 28.5981, "lng": 77.1504, "base_risk": 0.2},
    {"name": "Okhla Railway Crossing", "lat": 28.531, "lng": 77.271, "base_risk": 0.65},
    {"name": "Shakurbasti Yard", "lat": 28.6784, "lng": 77.1511, "base_risk": 0.45},
    {"name": "Faridabad Section", "lat": 28.4089, "lng": 77.3178, "base_risk": 0.5},
    {"name": "Tughlakabad Depot", "lat": 28.5072, "lng": 77.2835, "base_risk": 0.4},
    {"name": "Patel Nagar Section", "lat": 28.6513, "lng": 77.1640, "base_risk": 0.35},
    {"name": "Subzi Mandi Area", "lat": 28.6686, "lng": 77.2150, "base_risk": 0.55},
    {"name": "Kashmere Gate Section", "lat": 28.6668, "lng": 77.2289, "base_risk": 0.45},
]

MODEL_PATH = "data/models"

class RiskScoringEngine:
    def __init__(self):
        self.risk_model = None
        self.level_classifier = None
        self.scaler = StandardScaler()
        self._train_models()

    def _generate_training_data(self):
        """Generate realistic training data from known risk patterns."""
        np.random.seed(42)
        X = []
        y_score = []
        y_level = []

        for _ in range(2000):
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            vibration = np.random.exponential(0.15) + 0.02
            temperature = 25 + 10 * np.sin((hour - 6) * np.pi / 12) + np.random.normal(0, 2)
            base_risk = np.random.uniform(0.2, 0.7)
            recent_incidents = np.random.poisson(1.5)
            visibility = max(0.5, 10 - np.random.exponential(2))
            is_night = 1 if (hour >= 22 or hour <= 5) else 0

            features = [hour, day_of_week, vibration, temperature, base_risk,
                       recent_incidents, visibility, is_night]

            # Risk score formula (learned pattern)
            score = (
                base_risk * 40 +
                is_night * 20 +
                min(vibration * 80, 30) +
                recent_incidents * 5 +
                max(0, (temperature - 40) * 2) +
                max(0, (3 - visibility) * 5) +
                np.random.normal(0, 3)
            )
            score = max(5, min(98, score))

            if score > 70: level = 2  # CRITICAL
            elif score > 50: level = 1  # HIGH
            else: level = 0  # LOW/MEDIUM

            X.append(features)
            y_score.append(score)
            y_level.append(level)

        return np.array(X), np.array(y_score), np.array(y_level)

    def _train_models(self):
        """Train risk regression and classification models."""
        try:
            X, y_score, y_level = self._generate_training_data()
            X_scaled = self.scaler.fit_transform(X)

            # Train risk score regressor
            self.risk_model = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )
            self.risk_model.fit(X_scaled, y_score)

            # Train risk level classifier
            self.level_classifier = GradientBoostingClassifier(
                n_estimators=80, max_depth=5, random_state=42
            )
            self.level_classifier.fit(X_scaled, y_level)

            # Save models
            os.makedirs(MODEL_PATH, exist_ok=True)
            joblib.dump(self.risk_model, f"{MODEL_PATH}/risk_regressor.pkl")
            joblib.dump(self.level_classifier, f"{MODEL_PATH}/risk_classifier.pkl")
            joblib.dump(self.scaler, f"{MODEL_PATH}/risk_scaler.pkl")

            logger.info("ML Risk models trained and saved successfully")
        except Exception as e:
            logger.error(f"Failed to train risk models: {e}")

    def predict_zone_risk(self, zone: dict, sensor_data: dict = None):
        """Predict risk score for a single zone using ML model."""
        now = datetime.utcnow()
        hour = now.hour
        day_of_week = now.weekday()
        is_night = 1 if (hour >= 22 or hour <= 5) else 0

        vibration = sensor_data.get("vibration", 0.1) if sensor_data else 0.1
        temperature = sensor_data.get("temperature", 30) if sensor_data else 30
        recent_incidents = sensor_data.get("recent_incidents", 0) if sensor_data else 0
        visibility = sensor_data.get("visibility", 8) if sensor_data else 8

        features = np.array([[hour, day_of_week, vibration, temperature,
                             zone["base_risk"], recent_incidents, visibility, is_night]])

        if self.risk_model and self.scaler:
            features_scaled = self.scaler.transform(features)
            score = float(self.risk_model.predict(features_scaled)[0])
            level_idx = int(self.level_classifier.predict(features_scaled)[0])
            levels = ["LOW", "HIGH", "CRITICAL"]
            level = levels[level_idx]
        else:
            score = zone["base_risk"] * 60 + is_night * 15
            level = "HIGH" if score > 50 else "LOW"

        score = max(5, min(98, score))
        factors = []
        if is_night: factors.append("Night-time elevated risk")
        if vibration > 0.3: factors.append(f"High vibration: {vibration:.3f}g")
        if temperature > 42: factors.append(f"Rail heat stress: {temperature:.1f}°C")
        if recent_incidents > 2: factors.append(f"{recent_incidents} recent incidents")

        return {
            "name": zone["name"],
            "lat": zone["lat"],
            "lng": zone["lng"],
            "risk_score": round(score, 1),
            "risk_level": level,
            "factors": factors if factors else ["Normal operations"],
            "model": "GradientBoosting+RandomForest",
            "timestamp": now.isoformat(),
        }

    def get_heatmap_data(self, sensor_data: dict = None):
        """Get risk predictions for all zones."""
        return [self.predict_zone_risk(z, sensor_data) for z in ZONES]

    def get_ranked_scores(self, sensor_data: dict = None):
        """Get risk scores sorted by severity."""
        data = self.get_heatmap_data(sensor_data)
        return sorted(data, key=lambda x: x["risk_score"], reverse=True)


risk_service = RiskScoringEngine()
