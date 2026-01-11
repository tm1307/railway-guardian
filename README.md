Markdown

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
* **Phyphox Integration:** Uses smartphone accelerometers as IoT vibration sensors, streaming data over Wi-Fi.
* **Forensic Analysis:** Supports post-incident video uploads to analyze noise levels and visual threats.

### 3. 👷 Smart Operations API
* **Maintenance Awareness:** Simulates a connection to a Central Railway Server.
* **False Alarm Suppression:** If a "High Impact" event occurs during a scheduled work window, the system flags it as **"Authorized Maintenance"** (Blue Alert) instead of **"Sabotage"** (Red Alert).

### 4. 📂 Multiple Operating Modes
* **Simulation Mode:** Replays historical CSV data and injects synthetic "Sabotage" spikes for safe demos.
* **Real-Time Mode:** Connects to live sensors.

---

## 🛠️ System Architecture

```mermaid
graph TD
    %% Styling - VIVID THEME
    classDef input fill:#00b0ff,stroke:#001970,stroke-width:3px,color:white;
    classDef core fill:#00e676,stroke:#00600f,stroke-width:3px,color:black;
    classDef ai fill:#ff9100,stroke:#c56000,stroke-width:3px,color:black;
    classDef output fill:#d500f9,stroke:#4a0072,stroke-width:3px,color:white;

    subgraph INPUTS [📡 Data Sources]
        A1[IoT Sensor <br/>Phyphox/Phone] -->|HTTP/Wi-Fi| B1(Data Ingestion)
        A2[CCTV / Webcam <br/>Video Feed] -->|CV2 Capture| B1
        A3[Simulation / CSV <br/>Replay Data] -->|Pandas Read| B1
    end

    subgraph PROCESSING [🧠 The Core Engine]
        B1 --> C1{logic.py <br/> Fusion Engine}
        
        %% AI Models
        C1 <-->|Vibration Data| D1[Anomaly Model <br/> Isolation Forest]
        C1 <-->|Video Frame| D2[Vision Model <br/> YOLOv8]
        
        %% External Checks
        C1 <-->|Check Schedule| D3[Operations API <br/> maintenance.py]
    end

    subgraph UI [💻 Streamlit Dashboard]
        C1 -->|Annotated Frame| E1[Live Video Feed]
        C1 -->|Risk Score| E2[Real-time Graph]
        C1 -->|Status Color| E3[Alert System]
    end

    %% Apply Styles
    class A1,A2,A3 input;
    class B1,C1 core;
    class D1,D2,D3 ai;
    class E1,E2,E3 output;
🧠 Decision Logic (The Fusion Brain)
This flowchart explains how the system decides between "Sabotage," "Maintenance," and "Safe."

Code snippet

flowchart TD
    Start([New Data Frame]) --> Input{Get Inputs}
    
    Input -->|Vibration| VibCheck[Analyze Vibration]
    Input -->|Video| VisionCheck[Detect Objects]
    
    %% Parallel Processing
    Vibration --> AI_Vib[Isolation Forest Check]
    AI_Vib -->|Score < -0.05| HighVib[⚠️ Critical Vibration]
    AI_Vib -->|Score > -0.05| LowVib[✅ Stable]
    
    VisionCheck --> AI_Vis[YOLOv8 Scan]
    AI_Vis -->|Class 0| Human[👤 Person Detected]
    AI_Vis -->|Class 24/26/43| Tool[🧰 Tools Detected]
    AI_Vis -->|None| Empty[No Activity]

    %% Fusion Logic
    HighVib & Human --> Fusion{FUSION CHECK}
    HighVib & Empty --> MechCheck{Mech Fault Check}
    LowVib & Human --> TrespCheck{Trespass Check}

    %% Context Layer
    Fusion --> API_Check{Maintenance API <br/> Active?}
    
    %% Final Decisions
    API_Check -- YES --> Blue[🔵 AUTHORIZED MAINTENANCE <br/> System Suppressed]
    API_Check -- NO --> Red[🔴 SABOTAGE ALERT <br/> Human + High Impact]
    
    MechCheck --> Yellow[🟡 MECHANICAL FAULT <br/> Vibration without Person]
    TrespCheck --> Orange[🟠 TRESPASSING <br/> Person but Track Stable]

    %% VIVID STYLING
    style Start fill:#2979ff,stroke:#000,stroke-width:2px,color:#fff
    style Input fill:#2979ff,stroke:#000,stroke-width:2px,color:#fff
    
    style Red fill:#ff1744,stroke:#7f0000,stroke-width:4px,color:#fff
    style Blue fill:#00e5ff,stroke:#006064,stroke-width:4px,color:#000
    style Yellow fill:#ffea00,stroke:#ff6f00,stroke-width:3px,color:#000
    style Orange fill:#ff9100,stroke:#bf360c,stroke-width:3px,color:#000
    
    style VibCheck fill:#b0bec5,stroke:#333,color:#000
    style VisionCheck fill:#b0bec5,stroke:#333,color:#000
💻 Installation & Setup
1. Clone the Repository
Bash

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
