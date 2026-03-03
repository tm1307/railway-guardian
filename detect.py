"""
Standalone Anomaly Detector — CLI tool for batch vibration analysis.
Can be run independently to scan vibration data for tampering.

Usage:
    python detect.py
    python detect.py --threshold -0.1
"""

import pandas as pd
import joblib
import numpy as np
import os
import sys


MODEL_PATH = "models/anomaly_model.pkl"
DATA_PATH = "data/vibration_data.csv"
THRESHOLD = -0.05


def load_resources():
    """Safely load the anomaly detection model."""
    if not os.path.exists(MODEL_PATH):
        print(f"  ❌ Error: Model file not found at {MODEL_PATH}")
        return None
    model = joblib.load(MODEL_PATH)
    print(f"  ✅ Model loaded from {MODEL_PATH}")
    return model


def detect_tampering(model, signal, threshold=None):
    """Predict anomaly score for a single signal array."""
    thresh = threshold if threshold is not None else THRESHOLD
    signal = np.array(signal).reshape(1, -1)
    score = model.decision_function(signal)[0]

    if score < thresh:
        return "🚨 TAMPERING DETECTED", abs(score), "CRITICAL"
    elif score < 0:
        return "⚠️  Borderline Signal", abs(score), "CAUTION"
    else:
        return "✅ Normal Track", abs(score), "SAFE"


def print_header():
    print()
    print("=" * 60)
    print("  🛡️  RAILGUARD — Vibration Anomaly Scanner")
    print("=" * 60)
    print()


def main():
    print_header()

    # Parse optional threshold
    threshold = THRESHOLD
    if "--threshold" in sys.argv:
        idx = sys.argv.index("--threshold")
        if idx + 1 < len(sys.argv):
            try:
                threshold = float(sys.argv[idx + 1])
                print(f"  ⚙️  Custom threshold: {threshold}")
            except ValueError:
                print("  ⚠️  Invalid threshold, using default")

    # Load model
    model = load_resources()
    if model is None:
        return

    # Load data
    if not os.path.exists(DATA_PATH):
        print(f"  ❌ Error: Data file not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"  📂 Loaded vibration data: {len(df)} rows × {df.shape[1]} columns")
    print()

    # Single sample test
    sample_row_index = 120
    if len(df) > sample_row_index:
        sample = df.iloc[sample_row_index].drop("label", errors='ignore').values
        result, score, severity = detect_tampering(model, sample, threshold)
        print("  ─── Single Sample Test (Row 120) ───")
        print(f"  {result}")
        print(f"  Risk Score: {round(score, 4)} | Severity: {severity}")
        print()

    # Full dataset scan
    print("  ─── Full Dataset Scan ───")
    data_for_pred = df.drop(columns=['label'], errors='ignore')
    scores = model.decision_function(data_for_pred)

    anomalies = np.where(scores < threshold)[0]
    normal = len(df) - len(anomalies)
    pct = (len(anomalies) / len(df)) * 100 if len(df) > 0 else 0

    print(f"  🔍 Scanned: {len(df)} tracks")
    print(f"  ✅ Normal:  {normal}")
    print(f"  🚨 Anomalous: {len(anomalies)} ({pct:.1f}%)")

    if len(anomalies) > 0:
        print(f"  📍 Sample indices: {list(anomalies[:10])}")
        print(f"  📊 Anomaly score range: [{scores[anomalies].min():.4f}, {scores[anomalies].max():.4f}]")
    else:
        print("  ✅ No anomalies detected in the dataset.")

    print()
    print("  ─── Summary Report ───")
    print(f"  Model: {MODEL_PATH}")
    print(f"  Threshold: {threshold}")
    print(f"  Total scanned: {len(df)}")
    print(f"  Anomaly rate: {pct:.1f}%")
    print(f"  Score distribution: min={scores.min():.4f}, "
          f"mean={scores.mean():.4f}, max={scores.max():.4f}")
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()