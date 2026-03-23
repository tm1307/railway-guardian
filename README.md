# Railway Guardian: 

Railway Guardian is a comprehensive, production-ready Command, Control, Communications, Computers, Intelligence, Surveillance, and Reconnaissance (C4ISR) platform designed to secure and monitor Indian Railway infrastructure. 

This platform integrates real-time IoT sensors, AI-driven computer vision, and machine learning predictive analytics into a unified, high-performance dashboard featuring an authentic Indian Government NIC-inspired design system.

---

## 🌟 Core Features

### 1. Surveillance & Computer Vision (AI)
* **Live Webcam YOLOv8 Detection**: Real-time bounding boxes with tactical overlays (corner brackets, threat glow). Optimized to process frames via WebSocket, rendering at reliable FPS.
* **Video Upload Forensics**: Upload MP4/AVI files for asynchronous frame-sampled object detection and threat analysis using the same YOLOv8 model.
* **Threat Categorization**: Identifies distinct threats (persons on tracks, unrecognized objects) and summaries.

### 2. Live Sensor Telemetry (IoT)
* **Real Mobile Integration (Phyphox)**: Use a physical smartphone running the Phyphox app as a field sensor. Connect via local IP to stream raw X, Y, Z accelerometer data directly into the dashboard.
* **Smart Autonomous Scheduler**: Simulates highly realistic daily (diurnal) sinusoidal vibration and temperature patterns when real hardware is disconnected.
* **Automated Threshold Alerts**: Background jobs automatically generate alerts if vibration/temperature breach safety thresholds.

### 3. Machine Learning Intelligence
* **Risk Scoring Engine**: A `scikit-learn` Random Forest and Gradient Boosting pipeline trained on 2,000 specific data points to calculate dynamic risk scores for 15 railway zones based on time, temperature, incident history, and sensor metrics.
* **Intent Prediction Pipeline**: An advanced `scikit-learn` multiclass classifier trained on 3,000 synthetically generated historical patterns. Predicts "tampering", "theft", "vandalism", or "trespassing" based on a fusion of multisensory input.

### 4. Enterprise Maintenance Management
* **Maintenance Scheduler**: Full CRUD system to block out maintenance windows.
* **Alert Suppression**: The Intent Prediction AI is spatially aware. If a worker is detected in a zone with an active maintenance schedule, the AI intelligently suppresses the alert and marks the sector as "safe", preventing false positive fatigue.

### 5. Multi-Channel Real-Time Processing
* **100% Live Dashboard**: No static dummy data. Fast API WebSockets drive the alert feed, real-time Recharts line graphs, and KPI metrics.
* **Operator Broadcast**: Duty Operators can manually dispatch custom alerts with location and severity that instantly broadcast to all connected Admin and Viewer clients.

### 6. RoboSarthi AI Assistant
* A floating, customizable chat widget embedded globally in the application.

---

## 🛠 Tech Stack

**Backend System**
* **Framework**: Python 3, FastAPI, Uvicorn
* **Database**: SQLite (SQLAlchemy ORM) — Production ready for Postgres via `DATABASE_URL`
* **Real-time**: FastAPI WebSockets
* **AI/CV**: Ultralytics YOLOv8, OpenCV Headless
* **Machine Learning**: `scikit-learn`, `pandas`, `numpy`, `joblib`
* **Security**: JWT Authentication (Role-Based Access Control)

**Frontend Application**
* **Framework**: React 18, Vite
* **Routing**: React Router DOM (Protected Routes)
* **Data Fetching & API**: Axios (with JWT interceptors)
* **Visualizations**: Recharts (streaming data), Leaflet (Offline maps)
* **Styling**: Custom NIC-inspired styling (Vanilla CSS), Lucide React Icons

---

## 🚀 Getting Started

### 1. Backend Setup

```bash
# Navigate to project root
cd railway_tampering

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# (Optional) Regenerate ML Model Training Data
# This generates the CSV files the sklearn models were trained on
python -m backend.app.ml.generate_training_data

# Run the backend server
python3 -m uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
# Open a new terminal
cd railway_tampering/frontend

# Install dependencies
npm install

# Run Vite development server
npm run dev

# For Production Build:
npm run build
npm run preview
```

---

## 🔐 Default Credentials

The database seeds with three distinct user roles:

| Role | Username | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Admin** (Chief Security Officer) | `admin` | `admin123` | Full access, modify schedules, manage logic |
| **Operator** (Duty Controller) | `operator` | `operator123` | Broadcast manual alerts, manage active schedules |
| **Viewer** (RPF Inspector) | `viewer` | `viewer123` | Read-only observation dashboard |

---

## 📱 Hardware Emulation (Phyphox Integration)

To stream real sensor data instead of relying on the backend simulation:
1. Download **Phyphox** on your iOS/Android device.
2. Open the "Acceleration (without g)" experiment.
3. Open the three-dot menu and select "Allow Remote Access" (Note the given URL, e.g., `192.168.1.10:8080`).
4. Press the **Play** button on the phone.
5. In the Railway Guardian **Sensor Analytics** tab, enter the IP (without the `http://` part) and click **Connect**.
6. The dashboard charts and KPI nodes will flip to `<REAL>` and stream your physical movement.
