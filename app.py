import streamlit as st
import cv2
import numpy as np
import pandas as pd
import time
import tempfile
import logic
import maintenance


st.set_page_config(
    page_title="Railway Guardian Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
    <style>
        .stApp { background-color: #0E1117; }
        .css-1r6slb0, .css-12oz5g7 {
            background-color: #262730; border: 1px solid #41424C;
            padding: 20px; border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        div[data-testid="stMetricValue"] {
            font-size: 2.5rem !important; font-weight: 700; color: #00ADB5;
        }
        img { border: 2px solid #333; border-radius: 8px; }
        div[data-testid="stAlert"] { padding: 1rem; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/vibration_data.csv")
        if 'label' in df.columns: df = df.drop(columns=['label'])
        return df
    except: return None

df_csv = load_data()


st.sidebar.image("https://img.icons8.com/color/96/train.png", width=60)
st.sidebar.title("SYSTEM CONTROL")
st.sidebar.markdown("---")

# --- SECTION A: OPERATIONS API (Maintenance) ---
st.sidebar.subheader("👷 Operations API")
maint_mode = st.sidebar.toggle("Simulate Scheduled Work", value=False)
maintenance.toggle_maintenance("section_1", maint_mode)

if maint_mode:
    st.sidebar.info("✅ API Status: Work Order Active")
else:
    st.sidebar.caption("API Status: Normal Operations")

st.sidebar.markdown("---")

# --- SECTION B: DATA SOURCE (Vibration) ---
st.sidebar.subheader("📡 Vibration Source")
data_source = st.sidebar.radio(
    "Select Mode:", 
    ["Simulation", "Real-Time", "Forensic Analysis (Upload Video)"],
    label_visibility="collapsed"
)

# --- SAFETY VARIABLES (Prevent Crashes) ---
sim_mode = "Normal Track"
video_file_path = None
audio_levels = []

# --- CONFIG BASED ON SOURCE ---
if data_source == "Real-Time":
    # Shows only if Real-Time is selected
    default_ip = "192.168.1.10:8080"
    phone_ip = st.sidebar.text_input("Phyphox IP:", default_ip)
    if st.sidebar.button("🔗 Connect Sensor"):
        logic.set_phyphox_url(phone_ip)
        st.sidebar.success(f"Linked: {phone_ip}")
        
elif data_source == "Simulation":
    # Shows only if Simulation is selected
    st.sidebar.caption("Dataset: vibration_data.csv")
    sim_mode = st.sidebar.selectbox("⚡ Inject Scenario:", ["Normal Track", "Earthquake (High)", "Sabotage (Spikes)"])

elif data_source == "Forensic Analysis (Upload Video)":
    # Shows only if Forensic is selected
    st.sidebar.info("Upload MP4/AVI to analyze noise & tools.")
    uploaded_video = st.sidebar.file_uploader("Upload Video File", type=['mp4', 'avi', 'mov'])
    if uploaded_video:
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(uploaded_video.read())
        video_file_path = tfile.name
        with st.spinner("Extracting Audio Noise Profile..."):
            audio_levels = logic.extract_audio_intensity(video_file_path)
        st.sidebar.success(f"Profile Loaded ({len(audio_levels)} frames)")

st.sidebar.markdown("---")

# --- SECTION C: VISION SYSTEM (Camera) ---
st.sidebar.subheader("👁️ Vision Feed")

use_webcam = False
if data_source != "Forensic Analysis (Upload Video)":
    use_webcam = st.sidebar.toggle("Activate Laptop Webcam", value=True)
else:
    st.sidebar.caption("Source: File Upload")

st.sidebar.markdown("---")
st.sidebar.info("System Ready. Awaiting Activation.")

# --- 5. MAIN DASHBOARD ---
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title("🛡️ Railway Guardian AI")
    st.caption("Real-time Acoustic, Visual & Tool Detection System")
with col_header_2:
    status_indicator = st.empty()
    status_indicator.markdown("### ⚪ STANDBY")

col_main, col_stats = st.columns([2, 1])
with col_main:
    st.markdown("#### 📺 Visual Feed")
    video_placeholder = st.empty()
    video_placeholder.image("https://placehold.co/640x480/black/white?text=System+Offline", use_container_width=True)

with col_stats:
    st.markdown("#### 📊 Telemetry")
    with st.container():
        metric_placeholder = st.empty()
        metric_placeholder.metric("Noise/Vibration", "0.00", delta="0.00")
    
    st.markdown("#### 📉 Intensity Graph")
    chart_placeholder = st.empty()
    chart_placeholder.line_chart([0.0]*50, height=200)

alert_placeholder = st.empty()

if 'stream_index' not in st.session_state: st.session_state['stream_index'] = 0

# --- 6. EXECUTION LOOP ---
run_system = st.sidebar.checkbox("🚀 INITIATE SYSTEM", value=False)

if run_system:
    status_indicator.markdown("### 🟢 ONLINE")
    
    cap = None
    
    # CASE 1: Forensic Video File
    if data_source == "Forensic Analysis (Upload Video)" and video_file_path:
        cap = cv2.VideoCapture(video_file_path)
        
    # CASE 2: Live Laptop Webcam
    elif data_source != "Forensic Analysis (Upload Video)" and use_webcam:
        cap = cv2.VideoCapture(0)  
    
    chart_data = []
    frame_count = 0

    while run_system:
        # A. GET DATA (Noise/Vibration Level)
        vib_level = 0.0
        
        if data_source == "Real-Time (Phyphox iOS)":
            vib_level = logic.get_real_vibration()
            
        elif data_source == "Forensic Analysis (Upload Video)":
            if frame_count < len(audio_levels):
                vib_level = audio_levels[frame_count]
            else:
                vib_level = 0.0
                
        else: # Simulation (CSV Replay)
            if df_csv is not None and not df_csv.empty:
                idx = st.session_state['stream_index'] % len(df_csv)
                row = df_csv.iloc[idx].values
                base = np.mean(np.abs(row))
                
                # Injection Logic
                if sim_mode == "Normal Track": vib_level = base * 0.1
                elif sim_mode == "Earthquake (High)": vib_level = base + 0.6
                else: 
                    # Sabotage
                    if np.random.random() > 0.6: 
                        vib_level = base + np.random.uniform(0.5, 0.9)
                    else:
                        vib_level = base + 0.1
                
                st.session_state['stream_index'] += 1

        # B. GET VIDEO FRAME
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                # Loop video
                if data_source == "Forensic Analysis (Upload Video)":
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frame_count = 0
                    continue
                else:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # C. AI FUSION
        annotated_frame, alert_status, color, explanation = logic.detect_threats(frame, vib_level)

        # D. UI UPDATES
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        delta_color = "normal" if vib_level < 0.35 else "inverse"
        metric_placeholder.metric("Noise/Vibration", f"{vib_level:.2f}", delta=f"{vib_level:.2f}", delta_color=delta_color)

        chart_data.append(vib_level)
        if len(chart_data) > 50: chart_data.pop(0)
        chart_placeholder.line_chart(chart_data)

        if color == "red":
            status_indicator.markdown("### 🔴 CRITICAL")
            alert_placeholder.error(f"### 🚨 {alert_status}\n{explanation}", icon="🚨")
        elif color == "blue":
            status_indicator.markdown("### 🔵 MAINTENANCE")
            alert_placeholder.info(f"### ✅ {alert_status}\n{explanation}", icon="✅")
        elif color == "orange":
            status_indicator.markdown("### 🟠 WARNING")
            alert_placeholder.warning(f"### ⚠️ {alert_status}\n{explanation}", icon="⚠️")
        elif color == "yellow":
            status_indicator.markdown("### 🟡 CAUTION")
            alert_placeholder.warning(f"### 🔧 {alert_status}\n{explanation}", icon="🔧")
        else:
            status_indicator.markdown("### 🟢 SECURE")
            alert_placeholder.success(f"### ✅ {alert_status}\n{explanation}", icon="✅")

        frame_count += 1
        
        if data_source == "Forensic Analysis (Upload Video)":
            time.sleep(0.01)
        else:
            time.sleep(0.05)

    if cap: cap.release()
else:
    status_indicator.markdown("### ⚪ PAUSED")