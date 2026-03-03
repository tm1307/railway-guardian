"""
Model Training Script — Trains an Isolation Forest anomaly detection model
on vibration sensor data for RailGuard.

Usage:
    python train.py
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os
import datetime


DATA_PATH = "data/vibration_data.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_model.pkl")


def main():
    print()
    print("=" * 60)
    print("  🛡️  RAILGUARD — Model Training Pipeline")
    print("=" * 60)
    print()

    # 1. Load data
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"  ❌ Error: '{DATA_PATH}' not found!")
        return

    if "label" in df.columns:
        labels = df["label"]
        X = df.drop("label", axis=1)
    else:
        labels = None
        X = df

    print(f"  📂 Data loaded: {X.shape[0]} rows × {X.shape[1]} features")
    print(f"  📊 Value range: [{X.values.min():.4f}, {X.values.max():.4f}]")

    if labels is not None:
        unique, counts = np.unique(labels, return_counts=True)
        print(f"  🏷️  Labels: {dict(zip(unique.astype(int), counts))}")

    print()

    # 2. Train model
    print("  ⚙️  Training Isolation Forest...")
    contamination = 0.05
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
    )
    model.fit(X)
    print("  ✅ Training complete.")
    print()

    # 3. Evaluate
    print("  ─── Evaluation Metrics ───")
    scores = model.decision_function(X)
    predictions = model.predict(X)

    n_anomalies = (predictions == -1).sum()
    n_normal = (predictions == 1).sum()
    pct = (n_anomalies / len(X)) * 100

    print(f"  🔍 Total samples: {len(X)}")
    print(f"  ✅ Normal: {n_normal}")
    print(f"  🚨 Anomalies: {n_anomalies} ({pct:.1f}%)")
    print(f"  📊 Score distribution:")
    print(f"     Min:  {scores.min():.4f}")
    print(f"     Mean: {scores.mean():.4f}")
    print(f"     Max:  {scores.max():.4f}")
    print(f"     Std:  {scores.std():.4f}")

    if labels is not None:
        # Cross-reference with ground truth
        anomaly_indices = np.where(predictions == -1)[0]
        actual_anomalies = labels.iloc[anomaly_indices]
        if len(actual_anomalies) > 0:
            flagged_as_anomaly = (actual_anomalies == 1).sum()
            print(f"  🎯 Of {n_anomalies} flagged, "
                  f"{flagged_as_anomaly} match ground truth labels.")

    print()

    # 4. Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"  💾 Model saved: {MODEL_PATH}")

    # Also save versioned copy
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    versioned = os.path.join(MODEL_DIR, f"anomaly_model_{ts}.pkl")
    joblib.dump(model, versioned)
    print(f"  💾 Versioned copy: {versioned}")

    print()
    print("  ─── Training Summary ───")
    print(f"  Model: Isolation Forest")
    print(f"  Estimators: 100")
    print(f"  Contamination: {contamination}")
    print(f"  Data shape: {X.shape}")
    print(f"  Timestamp: {ts}")
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()