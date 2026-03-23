"""
Generate and save ML training datasets for risk scoring and intent prediction.
Run this once to create the CSV files that document what our models are trained on.

Usage: python -m backend.app.ml.generate_training_data
"""
import numpy as np
import pandas as pd
import os
import math

OUTPUT_DIR = "data/training"

def generate_risk_training_data():
    """Generate risk scoring training dataset."""
    np.random.seed(42)
    records = []

    for _ in range(2000):
        hour = np.random.randint(0, 24)
        day_of_week = np.random.randint(0, 7)
        vibration = np.random.exponential(0.15) + 0.02
        temperature = 25 + 10 * np.sin((hour - 6) * np.pi / 12) + np.random.normal(0, 2)
        base_risk = np.random.uniform(0.2, 0.7)
        recent_incidents = np.random.poisson(1.5)
        visibility = max(0.5, 10 - np.random.exponential(2))
        is_night = 1 if (hour >= 22 or hour <= 5) else 0

        # Label: risk score
        risk_score = (
            base_risk * 40 +
            is_night * 20 +
            min(vibration * 80, 30) +
            recent_incidents * 5 +
            max(0, (temperature - 40) * 2) +
            max(0, (3 - visibility) * 5) +
            np.random.normal(0, 3)
        )
        risk_score = max(5, min(98, risk_score))

        if risk_score > 70: level = "CRITICAL"
        elif risk_score > 50: level = "HIGH"
        else: level = "LOW"

        records.append({
            "hour": hour,
            "day_of_week": day_of_week,
            "vibration_g": round(vibration, 4),
            "temperature_c": round(temperature, 1),
            "base_zone_risk": round(base_risk, 3),
            "recent_incidents": recent_incidents,
            "visibility_km": round(visibility, 1),
            "is_night": is_night,
            "risk_score": round(risk_score, 1),
            "risk_level": level,
        })

    df = pd.DataFrame(records)
    path = os.path.join(OUTPUT_DIR, "risk_training_data.csv")
    df.to_csv(path, index=False)
    print(f"Risk training data saved: {path} ({len(df)} samples)")
    return df


def generate_intent_training_data():
    """Generate intent prediction training dataset."""
    np.random.seed(123)
    records = []

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

        # Label assignment based on threat patterns
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

        records.append({
            "hour": hour,
            "is_night": is_night,
            "vibration_g": round(vibration, 4),
            "temperature_c": round(temperature, 1),
            "acoustic_db": round(acoustic, 1),
            "strain_ue": round(strain, 1),
            "person_detected": person_detected,
            "object_detected": object_detected,
            "maintenance_active": maintenance_active,
            "recent_alerts": recent_alerts,
            "threat_label": label,
        })

    df = pd.DataFrame(records)
    path = os.path.join(OUTPUT_DIR, "intent_training_data.csv")
    df.to_csv(path, index=False)
    print(f"Intent training data saved: {path} ({len(df)} samples)")
    return df


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generate_risk_training_data()
    generate_intent_training_data()
    print("\nTraining datasets generated successfully!")
    print(f"Files saved in: {OUTPUT_DIR}/")
