### Intelligent Railway Track Theft & Tampering Detection System

RailGuard is a multi-modal AI-powered railway infrastructure monitoring system designed to detect track theft, sabotage, and intentional tampering in real time.

By combining computer vision and vibration anomaly detection, RailGuard identifies high-risk events before they escalate into derailments or large-scale infrastructure failures.

---

## 📌 Overview

Railway networks span thousands of kilometers, making continuous manual inspection impractical. Track component theft (fasteners, fishplates, rail sections), sabotage, and unauthorized tampering significantly increase derailment risks and infrastructure damage.

Traditional monitoring approaches rely on manual patrol and passive CCTV observation, resulting in delayed detection and high human dependency.

RailGuard introduces a predictive, automated surveillance framework that intelligently fuses multiple data sources to assess risk and generate real-time alerts.

---

## 💡 Key Features

- Real-time object detection using **YOLOv8**
- Vibration anomaly detection using **Isolation Forest**
- Multi-modal risk fusion engine
- Context-aware maintenance verification
- Severity-based alert classification
- Live monitoring dashboard (Streamlit)
- Annotated video feed with bounding boxes
- Real-time vibration intensity graph

---

## 🧠 Risk Classification

RailGuard classifies detected events into:

- **Authorized Maintenance** – Scheduled and verified activity
- **Trespassing** – Human detected without structural anomaly
- **Mechanical Fault** – Vibration anomaly without human presence
- **High-Risk Theft / Sabotage** – Human/tool detection with abnormal vibration

This significantly reduces false positives compared to traditional CCTV-only systems.

---

## 🏗 System Architecture

### 🔹 Input Layer
- CCTV / Webcam video feed
- Vibration sensor data (Phyphox / CSV simulation)
- Maintenance schedule API

### 🔹 Processing Layer
- Object Detection Model (YOLOv8)
- Anomaly Detection Model (Isolation Forest)
- Fusion Engine (`logic.py`)
- Risk Scoring & Classification

### 🔹 Output Layer
- Real-time dashboard
- Alert notifications
- Annotated video stream
- Risk score visualization

---

## 🛠 Technology Stack

- Python
- YOLOv8
- OpenCV
- Scikit-learn (Isolation Forest)
- Streamlit
- Pandas
- NumPy
- REST API Integration

---

## 📁 Project Structure


railway-guardian/
│
├── app.py # Streamlit dashboard
├── detect.py # YOLO-based object detection
├── logic.py # Fusion and risk classification logic
├── maintenance.py # Maintenance schedule verification
├── train.py # Model training (if applicable)
├── data/ # Dataset and vibration samples
├── models/ # Model configuration
├── requirements.txt # Dependencies
└── README.md


---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/railway-guardian.git
cd railway-guardian
2. Install Dependencies
pip install -r requirements.txt
3. Run the Application
streamlit run app.py
📊 Impact

Reduces detection latency from hours to seconds

Prevents derailments caused by theft and tampering

Minimizes infrastructure damage

Enables predictive infrastructure protection

Supports scalable deployment across high-risk railway zones

🔮 Future Enhancements

Time-series modeling using LSTM for vibration prediction

Edge AI deployment optimization

Centralized monitoring grid for multi-zone analysis

Automated reporting and analytics dashboard
