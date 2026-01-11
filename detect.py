
import pandas as pd
import joblib
import numpy as np
import os


MODEL_PATH = "models/anomaly_model.pkl"
DATA_PATH = "data/vibration_data.csv"
THRESHOLD = -0.05

def load_resources():
    """Safely load the model."""
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Model file not found at {MODEL_PATH}")
        return None
    return joblib.load(MODEL_PATH)

def detect_tampering(model, signal):
    """
    Predicts anomaly score for a single signal array.
    """
    signal = np.array(signal).reshape(1, -1)
    score = model.decision_function(signal)[0]

    if score < THRESHOLD:
        return "🚨 Tampering Detected", abs(score)
    else:
        return "✅ Normal Track", abs(score)

def main():
    
    model = load_resources()
    if model is None:
        return

    
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Data file not found at {DATA_PATH}")
        return
    
    df = pd.read_csv(DATA_PATH)
    print(f"📂 Loaded data with {len(df)} rows.")


    sample_row_index = 120
    if len(df) > sample_row_index:
        sample = df.iloc[sample_row_index].drop("label", errors='ignore').values
        result, score = detect_tampering(model, sample)
        print("\n--- Single Sample Test (Row 120) ---")
        print(f"{result} | Risk Score: {round(score, 3)}")
    
    print("\n--- Full Dataset Scan ---")
    
    data_for_pred = df.drop(columns=['label'], errors='ignore')
    
   
    scores = model.decision_function(data_for_pred)
    anomalies = np.where(scores < THRESHOLD)[0]
    
    print(f"🔍 Scanned {len(df)} tracks.")
    if len(anomalies) > 0:
        print(f"⚠️  Found {len(anomalies)} potential tampering incidents.")
        print(f"   (Indices: {anomalies[:5]} ...)") 
    else:
        print("✅ No anomalies detected in the entire dataset.")

if __name__ == "__main__":
    main()