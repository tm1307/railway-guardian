# 🚂 RailGuard — Intelligent Railway Track Theft & Tampering Detection System

> **AI-powered multi-modal surveillance framework** for real-time detection of track theft, sabotage, and unauthorized tampering across Indian railway infrastructure.

![Python](https://img.shields.io/badge/Python-3.9+-3b82f6?style=for-the-badge&logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Computer_Vision-ef4444?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-f59e0b?style=for-the-badge&logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Anomaly_Detection-22c55e?style=for-the-badge&logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Active-22c55e?style=for-the-badge)

---

## 📌 Problem Statement

Railway networks span thousands of kilometers across India, making continuous manual inspection impractical and expensive. Three critical threats cause the majority of infrastructure failures:

| Threat | Impact |
|---|---|
| **Track component theft** (fasteners, fishplates, rail sections) | Directly increases derailment risk |
| **Sabotage & intentional tampering** | Catastrophic infrastructure damage |
| **Unauthorized trespassing** | Worker safety and liability risk |

Traditional monitoring relies on manual patrol and passive CCTV observation — resulting in **delayed detection**, **high false positive rates**, and **complete human dependency**.

RailGuard solves this by introducing a **predictive, automated surveillance framework** that intelligently fuses computer vision and vibration data to assess risk and trigger alerts in real time.

---

## 💡 Key Features

- 🎯 **Real-time object detection** using YOLOv8 — detects humans, tools, and track components
- 📳 **Vibration anomaly detection** using Isolation Forest — flags abnormal mechanical signatures
- 🧠 **Multi-modal risk fusion engine** — combines vision + vibration for context-aware classification
- 📅 **Maintenance verification** — cross-references scheduled maintenance to suppress false alerts
- 🚨 **Severity-based alert classification** — 4-tier risk system from Authorized to High-Risk
- 📊 **Live Streamlit dashboard** — annotated video feed + real-time vibration graph
- 🔲 **Bounding box annotations** — visual overlay on detected objects in video stream

---

## 🧠 Risk Classification Engine

RailGuard classifies every detected event into one of four categories:

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAILGUARD RISK ENGINE                        │
├──────────────────────┬──────────────────┬───────────────────────┤
│ CLASSIFICATION       │ VISION SIGNAL    │ VIBRATION SIGNAL      │
├──────────────────────┼──────────────────┼───────────────────────┤
│ ✅ AUTHORIZED        │ Human detected   │ Normal                │
│    MAINTENANCE       │ + schedule match │                       │
├──────────────────────┼──────────────────┼───────────────────────┤
│ ⚠️  TRESPASSING      │ Human detected   │ Normal                │
│                      │ no schedule match│                       │
├──────────────────────┼──────────────────┼───────────────────────┤
│ 🔧 MECHANICAL FAULT  │ No human         │ ANOMALY detected      │
│                      │                  │                       │
├──────────────────────┼──────────────────┼───────────────────────┤
│ 🚨 HIGH-RISK THEFT   │ Human + tool     │ ANOMALY detected      │
│    / SABOTAGE        │ detected         │                       │
└──────────────────────┴──────────────────┴───────────────────────┘
```

This multi-modal approach **significantly reduces false positives** compared to traditional CCTV-only systems.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                              │
│  📹 CCTV / Webcam Feed    📳 Vibration Sensor    📅 Maintenance │
│  (video stream)           (Phyphox / CSV sim)    Schedule API   │
└──────────────┬──────────────────┬──────────────────┬───────────┘
               │                  │                  │
               ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                           │
│                                                                 │
│  ┌─────────────────┐      ┌──────────────────────┐             │
│  │   detect.py     │      │   anomaly model      │             │
│  │   YOLOv8        │      │   Isolation Forest   │             │
│  │   Object Det.   │      │   Vibration Analysis │             │
│  └────────┬────────┘      └──────────┬───────────┘             │
│           │                          │                          │
│           └──────────┬───────────────┘                         │
│                      ▼                                          │
│            ┌──────────────────┐   ┌────────────────────┐       │
│            │    logic.py      │◄──│  maintenance.py    │       │
│            │  Fusion Engine   │   │  Schedule Checker  │       │
│            │  Risk Scoring    │   └────────────────────┘       │
│            └────────┬─────────┘                                │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                              │
│  📊 Streamlit Dashboard    🔔 Alert Notifications               │
│  🎥 Annotated Video Feed   📈 Risk Score Visualization          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Object Detection | YOLOv8 | Detect humans, tools, track components |
| Anomaly Detection | Scikit-learn — Isolation Forest | Flag abnormal vibration patterns |
| Video Processing | OpenCV | Frame capture, annotation, streaming |
| Dashboard | Streamlit | Live monitoring UI |
| Data Handling | Pandas + NumPy | Vibration data processing |
| Vibration Input | Phyphox / CSV simulation | Sensor data source |
| API Integration | REST API | Maintenance schedule verification |
| Language | Python 3.9+ | Full stack |

---

## 📁 Project Structure

```
railway-guardian/
│
├── app.py                  # Streamlit dashboard — main entry point
├── detect.py               # YOLOv8 object detection module
├── logic.py                # Fusion engine + risk classification
├── maintenance.py          # Maintenance schedule verification
├── train.py                # Model training (optional)
│
├── data/
│   ├── vibration_samples/  # CSV vibration data for simulation
│   └── dataset/            # Training dataset (images + labels)
│
├── models/
│   └── config/             # YOLOv8 model configuration
│
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/railway-guardian.git
cd railway-guardian
```

### 2. Create virtual environment
```bash
python3 -m venv railguard-env
source railguard-env/bin/activate    # Mac/Linux
# OR
railguard-env\Scripts\activate       # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

### 5. Open in browser
```
http://localhost:8501
```

---

## 📦 Requirements

Create a `requirements.txt` with:

```
ultralytics
opencv-python
streamlit
scikit-learn
pandas
numpy
requests
```

---

## 🔌 How It Works

### Step 1 — Video Input
`detect.py` captures frames from webcam or CCTV feed and runs YOLOv8 inference. Detected objects (person, tool, rail component) are annotated with bounding boxes.

### Step 2 — Vibration Input
Vibration data is streamed from a Phyphox-enabled phone sensor or simulated via CSV. The Isolation Forest model flags readings that deviate significantly from the trained baseline.

### Step 3 — Fusion & Classification
`logic.py` receives outputs from both models and applies the 4-tier risk classification logic. It also queries `maintenance.py` to check if any scheduled work is active at that location.

### Step 4 — Alert & Display
The Streamlit dashboard in `app.py` renders the annotated video feed, real-time vibration graph, current risk level, and alert history — all updating live.

---

## 📊 Impact

| Metric | Traditional System | RailGuard |
|---|---|---|
| Detection latency | Hours (manual patrol) | Seconds (automated) |
| False positive rate | High (CCTV only) | Low (multi-modal fusion) |
| Coverage | Limited patrol zones | Continuous automated |
| Human dependency | High | Minimal |
| Derailment prevention | Reactive | Predictive |

---

## 🔮 Future Enhancements

- [ ] **LSTM time-series modeling** for vibration prediction and trend analysis
- [ ] **Edge AI deployment** — optimized inference on Raspberry Pi / Jetson Nano
- [ ] **Centralized monitoring grid** — multi-zone analysis from a single control center
- [ ] **Automated reporting** — daily PDF reports for railway authorities
- [ ] **SMS / Email alerts** — instant notification to field engineers
- [ ] **GPS tagging** — pinpoint exact location of detected incidents on a map
- [ ] **Night vision support** — IR camera integration for 24/7 coverage

---

## 🏛️ Target Deployment

| Organization | Application |
|---|---|
| Indian Railways | National network monitoring |
| RVNL | New line construction security |
| RITES | Infrastructure audit support |
| Metro Rail Corporations | Urban track monitoring |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">
  <strong>RailGuard — Protecting India's Railway Infrastructure</strong><br/>
  Built with Computer Vision + Anomaly Detection + Real-time Fusion<br/>
  YOLOv8 · Isolation Forest · Streamlit · OpenCV
</div>
