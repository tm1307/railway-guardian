# �️ RailGuard Pro — Intelligent Railway Track Theft & Tampering Detection

> **AI-powered multi-modal surveillance framework** for real-time detection of track theft, sabotage, and unauthorized tampering across Indian railway infrastructure.

![Python](https://img.shields.io/badge/Python-3.9+-3b82f6?style=for-the-badge&logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Computer_Vision-ef4444?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-f59e0b?style=for-the-badge&logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Anomaly_Detection-22c55e?style=for-the-badge&logo=scikit-learn)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-3b82f6?style=for-the-badge&logo=plotly)
![Status](https://img.shields.io/badge/Status-Active-22c55e?style=for-the-badge)

---

## ⚡ Quick Start

```bash
# Clone and run in 3 commands
git clone https://github.com/yourusername/railway-guardian.git
cd railway-guardian
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501** → Toggle "INITIATE SYSTEM" → Watch it work!

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

## 🏆 What Makes RailGuard Different

| Feature | Traditional CCTV | RailGuard Pro |
|---|---|---|
| **Detection Model** | Single-modal (video only) | Multi-modal (vision + vibration + audio) |
| **Risk Assessment** | Binary (alert / no alert) | Quantitative 0–100 risk score |
| **False Positive Rate** | High | Low (fusion-based suppression) |
| **Maintenance Awareness** | None | Integrated schedule API |
| **Response Time** | Minutes to hours | Real-time (< 1 second) |
| **Explainability** | None | Detailed reasoning per alert |
| **Evidence Chain** | None | SHA-256 hashed forensic reports |
| **Zone Awareness** | None | GPS-based restricted area monitoring |
| **Prediction** | Reactive only | Escalation detection + time-to-breach |
| **Threat Analytics** | None | SOC-style pattern analysis dashboard |

---

## 💡 Key Features

- 🎯 **Real-time object detection** using YOLOv8 — detects humans, tools, and track components
- 📳 **Vibration anomaly detection** using Isolation Forest — flags abnormal mechanical signatures
- 🧠 **Multi-modal risk fusion engine** — combines vision + vibration for context-aware classification
- 📊 **Numerical risk scoring (0–100)** — quantitative threat assessment with weighted factors
- 📅 **Maintenance verification** — cross-references scheduled maintenance to suppress false alerts
- 🚨 **5-tier alert classification** — SAFE → INFO → CAUTION → WARNING → CRITICAL
- 🏛️ **RDSO-Compliant Evidence Chain** (Govt) — tamper-proof incident reports with SHA-256 integrity hashing, RDSO classification codes, and legal admissibility for railway safety audits
- �️ **Critical Infrastructure Protection Zones** (Govt) — GPS-based zone classification for bridges, tunnels, and defence corridors with automatic risk amplification and clearance levels
- 🤖 **AI-Powered Predictive Intelligence** (Innovation) — sliding-window trend analysis that predicts ESCALATING threats before they become critical, with time-to-breach estimates for preemptive RPF dispatch
- 🏛️ **Railway Operations Intelligence** (Govt) — command center analytics with severity distribution, risk trends, and incident classification for resource allocation and patrol scheduling
- 📋 **Persistent alert history** — timestamped incident log with CSV audit trail
- 🎯 **Detection confidence tracking** — real-time YOLO confidence overlay
- 📈 **Premium Plotly dashboard** — 4-tab layout: Live Monitor, Operations Intelligence, RDSO Evidence, Infrastructure Zones
- 🔲 **Bounding box annotations** — visual overlay on detected objects in video stream

---

## 🧠 Risk Classification Engine

RailGuard classifies every detected event using a **weighted multi-factor scoring** system:

```
┌─────────────────────────────────────────────────────────────────┐
│                   RAILGUARD RISK ENGINE v2.0                    │
├──────────────────────┬──────────────────┬───────────────────────┤
│ CLASSIFICATION       │ RISK SCORE       │ TRIGGER CONDITIONS    │
├──────────────────────┼──────────────────┼───────────────────────┤
│ ✅ SAFE              │ 0 – 14           │ No detections         │
├──────────────────────┼──────────────────┼───────────────────────┤
│ ℹ️  INFO              │ 15 – 24          │ Minor signals         │
├──────────────────────┼──────────────────┼───────────────────────┤
│ ⚠️  CAUTION           │ 25 – 44          │ Person OR tools       │
├──────────────────────┼──────────────────┼───────────────────────┤
│ 🟠 WARNING           │ 45 – 69          │ Person + tools OR     │
│                      │                  │ high vibration        │
├──────────────────────┼──────────────────┼───────────────────────┤
│ � CRITICAL          │ 70 – 100         │ Person + vibration    │
│                      │                  │ anomaly (sabotage)    │
├──────────────────────┼──────────────────┼───────────────────────┤
│ � MAINTENANCE       │ Score × 0.15     │ Scheduled work active │
│    (suppressed)      │                  │ → 85% risk reduction  │
└──────────────────────┴──────────────────┴───────────────────────┘
```

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
│  │   YOLOv8n       │      │   Isolation Forest   │             │
│  │   Object Det.   │      │   Vibration Anomaly  │             │
│  │   + Confidence  │      │   + Risk Scoring     │             │
│  └────────┬────────┘      └──────────┬───────────┘             │
│           │                          │                          │
│           └──────────┬───────────────┘                         │
│                      ▼                                          │
│            ┌──────────────────┐   ┌────────────────────┐       │
│            │    Fusion Engine │◄──│  Maintenance API   │       │
│            │  Weighted Risk   │   │  Multi-Section     │       │
│            │  Score (0-100)   │   │  Time-Window Sched │       │
│            └────────┬─────────┘   └────────────────────┘       │
│                     │                                           │
│            ┌────────▼─────────┐                                │
│            │  Alert Logger    │                                │
│            │  CSV + In-Memory │                                │
│            └────────┬─────────┘                                │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                              │
│  📊 Plotly Dashboard       🔔 Alert History & Notifications     │
│  🎯 Risk Gauge             📈 Vibration Waveform               │
│  � KPI Metrics            💾 CSV Export                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Object Detection | YOLOv8n | Detect humans, tools, track components |
| Anomaly Detection | Scikit-learn — Isolation Forest | Flag abnormal vibration patterns |
| Video Processing | OpenCV | Frame capture, annotation, streaming |
| Dashboard | Streamlit + Plotly | Premium live monitoring UI |
| Data Handling | Pandas + NumPy | Vibration data processing |
| Visualization | Plotly | Risk gauge, vibration charts |
| Alert Logging | Custom CSV Logger | Persistent incident tracking |
| Vibration Input | Phyphox / CSV simulation | Sensor data source |
| API Integration | REST API | Maintenance schedule verification |
| Language | Python 3.9+ | Full stack |

---

## 📁 Project Structure

```
railway-guardian/
│
├── app.py                  # Streamlit dashboard — 4-tab premium UI
├── logic.py                # Fusion engine + risk scoring (0-100)
├── detect.py               # Standalone CLI anomaly scanner
├── train.py                # Model training with evaluation
├── maintenance.py          # Multi-section maintenance API
├── alert_logger.py         # Alert logging + threat analytics
├── forensics.py            # SHA-256 forensic evidence chain
├── geo_zones.py            # GPS-based zone intrusion detection
├── predictor.py            # Predictive early warning system
├── test_smoke.py           # 11-test verification suite
│
├── data/
│   ├── vibration_data.csv  # Vibration sensor data (151 samples)
│   └── evidence/           # Auto-generated forensic reports
│
├── models/
│   ├── anomaly_model.pkl   # Trained Isolation Forest model
│   └── yolo/               # YOLOv8 model weights
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

## 🎮 Demo Guide

### Simulation Mode (No hardware needed)
1. Launch the dashboard: `streamlit run app.py`
2. Select **Simulation** from the sidebar
3. Choose **Sabotage (Spikes)** to see alerts trigger
4. Check **🚀 INITIATE SYSTEM** to start
5. Watch the risk gauge, alert history, and vibration chart update live

### CLI Anomaly Scanner
```bash
python detect.py                    # Run with defaults
python detect.py --threshold -0.1   # Custom sensitivity
```

### Train a New Model
```bash
python train.py
```

---

## 📦 Requirements

```
numpy
pandas
matplotlib
scikit-learn
streamlit
joblib
ultralytics
opencv-python-headless
plotly
requests
moviepy<2.0
```

---

## 🔌 How It Works

### Step 1 — Video Input
`logic.py` captures frames from webcam or CCTV feed and runs YOLOv8 inference. Detected objects (person, tool, rail component) are annotated with bounding boxes and confidence scores.

### Step 2 — Vibration Input
Vibration data is streamed from a Phyphox-enabled phone sensor or simulated via CSV. The Isolation Forest model flags readings that deviate significantly from the trained baseline.

### Step 3 — Fusion & Risk Scoring
The fusion engine combines vision and vibration signals using weighted factors to compute a **numerical risk score (0–100)**. It cross-references `maintenance.py` to suppress false positives during authorized work (85% risk reduction).

### Step 4 — Alert, Log & Display
Every non-normal event is logged to `alert_logger.py` (in-memory + CSV). The premium Streamlit dashboard renders the risk gauge, annotated video feed, vibration waveform, KPI metrics, and scrollable alert history — all updating in real time.

---

## 📊 Impact

| Metric | Traditional System | RailGuard Pro |
|---|---|---|
| Detection latency | Hours (manual patrol) | **< 1 second** (automated) |
| False positive rate | High (CCTV only) | **Low** (multi-modal fusion) |
| Risk assessment | Binary (alert/none) | **0–100 numerical score** |
| Coverage | Limited patrol zones | **Continuous automated** |
| Human dependency | High | **Minimal** |
| Derailment prevention | Reactive | **Predictive** |

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
  <strong>RailGuard Pro — Protecting India's Railway Infrastructure</strong><br/>
  Multi-Modal AI Surveillance • Quantitative Risk Scoring • Real-Time Fusion<br/>
  YOLOv8 · Isolation Forest · Streamlit · Plotly · OpenCV
</div>
