🚆 RailGuard
Intelligent Railway Track Theft & Tampering Detection System

RailGuard is a multi-modal AI surveillance system designed to detect railway track theft, sabotage, and structural tampering in real time.

It combines computer vision and vibration anomaly detection to identify high-risk events before they escalate into derailments.

Problem

Railway infrastructure spans thousands of kilometers, making continuous manual inspection impractical.

Track component theft (fasteners, fishplates, rail sections), sabotage, and unauthorized tampering significantly increase derailment risk.

Existing systems rely on:

Manual patrol

Passive CCTV monitoring

Post-incident investigation

These approaches are reactive, human-dependent, and lack contextual intelligence.

Solution

RailGuard introduces a predictive, automated monitoring framework that fuses:

🎥 Real-time object detection (YOLOv8)

📈 Vibration anomaly detection (Isolation Forest)

🧠 Context-aware risk classification logic

The system evaluates intent — not just presence — and generates severity-based alerts.

Core Capabilities

Real-time human and tool detection

Structural vibration anomaly detection

Multi-modal fusion engine

Maintenance schedule verification

Risk scoring & classification

Live monitoring dashboard

Annotated video output

Alert generation system

Risk Classification

RailGuard intelligently classifies events into:

Authorized Maintenance

Trespassing

Mechanical Fault

High-Risk Theft / Sabotage

This significantly reduces false positives compared to traditional CCTV systems.

System Architecture

Input Layer

CCTV / Webcam feed

Vibration sensor data (Phyphox / CSV)

Maintenance schedule data

Processing Layer

YOLOv8 detection pipeline

Isolation Forest anomaly model

Fusion engine (logic.py)

Risk classification module

Output Layer

Streamlit dashboard

Real-time alerts

Risk score visualization

Annotated video stream

Tech Stack

Python

YOLOv8

OpenCV

Scikit-learn (Isolation Forest)

Streamlit

Pandas / NumPy

Project Structure
railway-guardian/
│
├── app.py
├── detect.py
├── logic.py
├── maintenance.py
├── train.py
├── data/
├── models/
├── requirements.txt
└── README.md
Running the Project

Clone the repository:

git clone https://github.com/yourusername/railway-guardian.git
cd railway-guardian

Install dependencies:

pip install -r requirements.txt

Run the dashboard:

streamlit run app.py
Design Principles

Modular architecture

Hardware-agnostic deployment

Low-latency inference

Reduced false positives

Scalable across high-risk zones

Future Enhancements

Time-series vibration modeling (LSTM)

Edge AI deployment optimization

Multi-zone centralized monitoring

Automated reporting & analytics
