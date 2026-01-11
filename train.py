import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

try:
    df = pd.read_csv("data/vibration_data.csv")
except FileNotFoundError:
    print("❌ Error: 'data/vibration_data.csv' is missing!")
    exit()


if "label" in df.columns:
    X = df.drop("label", axis=1)
else:
    X = df

print(f"⚙️  Training model on {len(df)} rows...")


model = IsolationForest(
    n_estimators=100,
    contamination=0.05,  
    random_state=42
)

model.fit(X)


joblib.dump(model, "models/anomaly_model.pkl")

print("✅ Anomaly Detection Model trained & saved to 'models/anomaly_model.pkl'")