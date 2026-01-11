# 🛡️ Railway Guardian Pro: AI Fusion Security System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-green)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

**Railway Guardian Pro** is an intelligent, multi-modal security system designed to detect railway sabotage, trespassing, and mechanical faults in real-time.

It uses a **Sensor Fusion** approach, combining **Computer Vision (YOLOv8)** with **IoT Vibration Analysis (Isolation Forest)** to distinguish between authorized maintenance and actual threats.

---

## 🚀 Key Features

### 1. 🧠 AI Fusion Engine
Combines two distinct AI models to prevent false positives:
* **Visual Intelligence:** Detects Humans and Tools (Crowbars, Saws, Backpacks) using **YOLOv8**.
* **Vibration Analysis:** Detects drilling, sawing, or hammering impacts using **Isolation Forest** (Unsupervised Learning).

### 2. 📡 IoT & Remote Sensing
* **Wireless CCTV:** Turns any smartphone into a remote IP Camera for live surveillance.
* **Phyphox Integration:** Uses smartphone accelerometers as IoT vibration sensors, streaming data over Wi-Fi.

### 3. 👷 Smart Operations API
* **Maintenance Awareness:** Simulates a connection to a Central Railway Server.
* **False Alarm Suppression:** If a "High Impact" event occurs during a scheduled work window, the system flags it as **"Authorized Maintenance"** (Blue Alert) instead of **"Sabotage"** (Red Alert).

### 4. 📂 Multiple Operating Modes
* **Simulation Mode:** Replays historical CSV data and injects synthetic "Sabotage" spikes for safe demos.
* **Forensic Mode:** Uploads post-incident video footage to analyze audio noise levels and detect tools.

---

git clone [https://github.com/YOUR_USERNAME/railway-guardian.git](https://github.com/YOUR_USERNAME/railway-guardian.git)
cd railway-guardian
2. Install Dependencies
Bash

pip install -r requirements.txt
3. Run the Training Script (First Time Only)
Generates the anomaly_model.pkl file based on your dataset.

Bash

python train.py
4. Launch the Dashboard
Bash

streamlit run app.py
📱 How to Run the Demo (Phone Integration)
To use the Real-Time features, your laptop and phone must be on the same Wi-Fi network (or Mobile Hotspot).

A. Vibration Sensor (Phyphox)
Install Phyphox (Android/iOS).

Open "Acceleration with g".

Tap Menu (⋮) > Enable Remote Access.

Enter the displayed URL into the Streamlit Sidebar (e.g., http://192.168.1.5:8080).

B. Wireless CCTV (Optional)
Install IP Webcam (Android) or IP Camera Lite (iOS).

Start the server on the app.

Select "Wireless CCTV" in the Streamlit Sidebar.

Enter the URL (e.g., http://192.168.1.5:8080/video).

📂 Project Structure
Plaintext

railway-guardian/
├── app.py               # Main Streamlit Dashboard
├── logic.py             # AI Fusion Logic & Detection Engine
├── maintenance.py       # Mock Operations API
├── train.py             # ML Model Training Script
├── requirements.txt     # Python Dependencies
├── .gitignore           # Ignored files (venv, videos)
├── models/              # Saved .pkl models
└── data/                # Dataset (vibration_data.csv)


🛡️ License
This project is for educational and prototype purposes.
