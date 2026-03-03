"""
RailGuard Pro — Intelligent Railway Surveillance Dashboard v2.1
Premium Streamlit interface with tabbed layout:
  🔴 Live Monitor — real-time threat detection
  📊 Threat Intelligence — analytics & pattern analysis
  🔐 Forensics — tamper-proof evidence chain
  🗺️ Geo-Zones — restricted area monitoring
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import tempfile
import datetime

import logic
import maintenance
import alert_logger
import forensics
import geo_zones
import predictor

# ─── Predictive Engine Instance ────────────────────────────────────
if 'pred_engine' not in st.session_state:
    st.session_state['pred_engine'] = predictor.PredictiveEngine()

pred_engine = st.session_state['pred_engine']

# ─── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="RailGuard Pro — Railway Guardian AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Dark theme base ── */
    .stApp {
        background: linear-gradient(135deg, #06080d 0%, #0c1220 50%, #080e1a 100%);
        font-family: 'Inter', sans-serif;
    }

    /* ── Header gradient with animated border ── */
    .hero-header {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 16px;
        border: 1px solid rgba(0, 173, 181, 0.25);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 60px rgba(0, 173, 181, 0.05);
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 200%; height: 2px;
        background: linear-gradient(90deg, transparent, #00ADB5, transparent);
        animation: headerScan 4s linear infinite;
    }
    @keyframes headerScan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    .hero-header h1 {
        margin: 0;
        font-size: 1.7rem;
        background: linear-gradient(90deg, #00ADB5, #6dd5ed, #00e6c3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .hero-header p {
        color: #6b8299;
        margin: 4px 0 0 0;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0, 173, 181, 0.15) !important;
        border-bottom: 2px solid #00ADB5 !important;
    }

    /* ── Glassmorphism panels ── */
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
    }

    /* ── KPI cards ── */
    .kpi-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 12px 16px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        border-color: rgba(0, 173, 181, 0.3);
        box-shadow: 0 4px 20px rgba(0, 173, 181, 0.1);
    }
    .kpi-card .kpi-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00ADB5;
    }
    .kpi-card .kpi-label {
        font-size: 0.65rem;
        color: #506070;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-top: 2px;
    }

    /* ── Status indicators ── */
    .status-badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        letter-spacing: 1px;
    }
    .status-online   { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
    .status-critical  { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25);
                       animation: criticalPulse 1.5s ease-in-out infinite; }
    .status-warning  { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }
    .status-standby  { background: rgba(107,114,128,0.12); color: #9ca3af; border: 1px solid rgba(107,114,128,0.25); }

    @keyframes criticalPulse {
        0%, 100% { box-shadow: 0 0 8px rgba(239,68,68,0.3); }
        50% { box-shadow: 0 0 20px rgba(239,68,68,0.6); }
    }

    /* ── Alert history entries ── */
    .alert-entry {
        background: rgba(255,255,255,0.02);
        border-left: 3px solid #374151;
        padding: 6px 10px;
        margin: 3px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.75rem;
        transition: background 0.2s;
    }
    .alert-entry:hover { background: rgba(255,255,255,0.05); }
    .alert-entry.critical { border-left-color: #ef4444; }
    .alert-entry.warning  { border-left-color: #f59e0b; }
    .alert-entry.caution  { border-left-color: #eab308; }
    .alert-entry.info     { border-left-color: #3b82f6; }
    .alert-entry .alert-time { color: #506070; font-size: 0.65rem; }
    .alert-entry .alert-text { color: #c8d0d8; }

    /* ── Zone indicator ── */
    .zone-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }
    .zone-safe       { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
    .zone-buffer     { background: rgba(234,179,8,0.12); color: #eab308; border: 1px solid rgba(234,179,8,0.25); }
    .zone-restricted { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }

    /* ── Evidence row ── */
    .evidence-row {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 10px 14px;
        margin: 4px 0;
        font-size: 0.78rem;
    }
    .evidence-row .eid { color: #00ADB5; font-weight: 600; }
    .evidence-row .hash { color: #506070; font-family: monospace; font-size: 0.7rem; }

    /* ── Prediction indicator ── */
    .pred-badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.75rem;
    }
    .pred-escalating   { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25);
                         animation: criticalPulse 1.5s ease-in-out infinite; }
    .pred-stable       { background: rgba(59,130,246,0.12); color: #3b82f6; border: 1px solid rgba(59,130,246,0.25); }
    .pred-deescalating { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
    .pred-calibrating  { background: rgba(107,114,128,0.12); color: #9ca3af; border: 1px solid rgba(107,114,128,0.25); }

    /* ── Metric overrides ── */
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700; color: #00ADB5; }

    /* ── Image borders ── */
    img { border: 2px solid rgba(255,255,255,0.05); border-radius: 10px; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: rgba(8, 12, 20, 0.97);
        border-right: 1px solid rgba(255,255,255,0.04);
    }

    /* ── Footer ── */
    .system-footer {
        background: rgba(255,255,255,0.015);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 10px 16px;
        margin-top: 12px;
        color: #3d4d5d;
        font-size: 0.7rem;
        font-family: 'Inter', monospace;
    }

    /* ── Zone track map ── */
    .zone-track {
        display: flex;
        border-radius: 8px;
        overflow: hidden;
        height: 28px;
        margin: 8px 0;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .zone-seg {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.6rem;
        font-weight: 600;
        color: rgba(255,255,255,0.7);
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Load Vibration Data ────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/vibration_data.csv")
        if 'label' in df.columns:
            df = df.drop(columns=['label'])
        return df
    except Exception:
        return None


df_csv = load_data()


# ─── Plotly Builders ─────────────────────────────────────────────────
def create_risk_gauge(risk_score):
    if risk_score >= 70:
        bar_color = "#ef4444"
    elif risk_score >= 40:
        bar_color = "#f59e0b"
    elif risk_score >= 15:
        bar_color = "#eab308"
    else:
        bar_color = "#22c55e"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        number={"suffix": "", "font": {"size": 32, "color": "#e5e7eb"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#374151",
                     "tickfont": {"color": "#506070", "size": 9}},
            "bar": {"color": bar_color, "thickness": 0.75},
            "bgcolor": "rgba(255,255,255,0.02)",
            "borderwidth": 1, "bordercolor": "#1e293b",
            "steps": [
                {"range": [0, 15], "color": "rgba(34,197,94,0.08)"},
                {"range": [15, 40], "color": "rgba(234,179,8,0.08)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.08)"},
                {"range": [70, 100], "color": "rgba(239,68,68,0.08)"},
            ],
            "threshold": {"line": {"color": "#ef4444", "width": 2}, "thickness": 0.8, "value": 70},
        },
    ))
    fig.update_layout(height=180, margin=dict(l=15, r=15, t=25, b=5),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font={"color": "#e5e7eb"})
    return fig


def create_vibration_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data, mode='lines',
        line=dict(color='#00ADB5', width=2, shape='spline'),
        fill='tozeroy', fillcolor='rgba(0,173,181,0.06)', name='Vibration',
    ))
    fig.update_layout(
        height=160, margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)",
                   showticklabels=True, tickfont=dict(color="#3d4d5d", size=9), zeroline=False),
        showlegend=False,
    )
    fig.add_hline(y=0.35, line_dash="dash", line_color="rgba(239,68,68,0.3)",
                  annotation_text="Threshold", annotation_font_color="#506070",
                  annotation_font_size=9)
    return fig


def create_zone_map_html(zone_data):
    """Build an HTML zone track map with position marker."""
    zones = zone_data["zones"]
    current_km = zone_data["current_km"]
    total_km = zone_data["total_km"]

    html = '<div class="zone-track">'
    for z in zones:
        width_pct = ((z["km_end"] - z["km_start"]) / total_km) * 100
        zone_colors = {"safe": "rgba(34,197,94,0.2)", "buffer": "rgba(234,179,8,0.2)",
                       "restricted": "rgba(239,68,68,0.2)"}
        bg = zone_colors.get(z["type"], "rgba(128,128,128,0.2)")

        # Check if train is in this zone
        is_here = z["km_start"] <= current_km < z["km_end"]
        if is_here:
            bg = bg.replace("0.2", "0.5")

        marker = "🚂" if is_here else z["icon"]
        html += (f'<div class="zone-seg" style="width:{width_pct}%; background:{bg};">'
                 f'{marker} {z["id"]}</div>')

    html += '</div>'
    return html


# ═══════════════════════════════════════════════════════════════════
#                           SIDEBAR
# ═══════════════════════════════════════════════════════════════════

st.sidebar.markdown("### 🛡️ RAILGUARD PRO")
st.sidebar.caption("v2.1 · Advanced Threat Intelligence")
st.sidebar.markdown("---")

# ── Operations ──
st.sidebar.subheader("👷 Operations API")
maint_mode = st.sidebar.toggle("Simulate Scheduled Work", value=False)
maintenance.toggle_maintenance("section_1", maint_mode)
if maint_mode:
    st.sidebar.info("✅ Work Order Active — Team A deployed")
st.sidebar.markdown("---")

# ── Vibration Source ──
st.sidebar.subheader("📡 Vibration Source")
data_source = st.sidebar.radio(
    "Select Mode:",
    ["Simulation", "Real-Time", "Forensic Analysis (Upload Video)"],
    label_visibility="collapsed",
)

sim_mode = "Normal Track"
video_file_path = None
audio_levels = []

if data_source == "Real-Time":
    default_ip = "192.168.1.10:8080"
    phone_ip = st.sidebar.text_input("Phyphox IP:", default_ip)
    if st.sidebar.button("🔗 Connect Sensor"):
        logic.set_phyphox_url(phone_ip)
        st.sidebar.success(f"Linked: {phone_ip}")

elif data_source == "Simulation":
    st.sidebar.caption("Dataset: vibration_data.csv")
    sim_mode = st.sidebar.selectbox(
        "⚡ Inject Scenario:",
        ["Normal Track", "Earthquake (High)", "Sabotage (Spikes)"],
    )

elif data_source == "Forensic Analysis (Upload Video)":
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

# ── Vision ──
st.sidebar.subheader("👁️ Vision Feed")
use_webcam = False
if data_source != "Forensic Analysis (Upload Video)":
    use_webcam = st.sidebar.toggle("Activate Laptop Webcam", value=True)
else:
    st.sidebar.caption("Source: File Upload")

st.sidebar.markdown("---")
run_system = st.sidebar.checkbox("🚀 INITIATE SYSTEM", value=False)
st.sidebar.markdown("---")
st.sidebar.caption(f"RailGuard Pro v2.1 • {datetime.datetime.now().strftime('%Y-%m-%d')}")


# ═══════════════════════════════════════════════════════════════════
#                        MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════

# ── Hero Header ──
st.markdown("""
<div class="hero-header">
    <h1>🛡️ RailGuard Pro — Railway Guardian AI</h1>
    <p>Smart Railway Governance • Critical Infrastructure Protection • RDSO-Compliant Evidence • Predictive Intelligence</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Row (6 cards) ──
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpi_risk = k1.empty()
kpi_alerts = k2.empty()
kpi_uptime = k3.empty()
kpi_confidence = k4.empty()
kpi_zone = k5.empty()
kpi_prediction = k6.empty()

kpi_risk.metric("⚡ Risk", "0 / 100")
kpi_alerts.metric("🚨 Alerts", "0")
kpi_uptime.metric("⏱️ Uptime", "00:00")
kpi_confidence.metric("🎯 Conf.", "—")
kpi_zone.metric("🗺️ Zone", "—")
kpi_prediction.metric("🤖 Trend", "—")

# ── Status Bar ──
status_indicator = st.empty()
status_indicator.markdown(
    '<div style="text-align:center"><span class="status-badge status-standby">⚪ STANDBY</span></div>',
    unsafe_allow_html=True,
)

# ── Tabbed Interface ──
tab_live, tab_intel, tab_forensics, tab_zones = st.tabs([
    "🔴 Live Monitor", "🏛️ Operations Intelligence", "🏛️ RDSO Evidence", "🛡️ Infrastructure Zones"
])


# ─── TAB 1: LIVE MONITOR ───────────────────────────────────────────
with tab_live:
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.markdown("#### 📺 Live Visual Feed")
        video_placeholder = st.empty()
        video_placeholder.image(
            "https://placehold.co/640x480/06080d/1e293b?text=SYSTEM+OFFLINE",
            use_container_width=True,
        )

    with col_side:
        st.markdown("#### 🎯 Risk Gauge")
        gauge_placeholder = st.empty()
        gauge_placeholder.plotly_chart(create_risk_gauge(0), use_container_width=True, key="gauge_init")

        st.markdown("#### 📉 Vibration Waveform")
        chart_placeholder = st.empty()
        chart_placeholder.plotly_chart(create_vibration_chart([0.0] * 50),
                                      use_container_width=True, key="chart_init")

        st.markdown("#### 🤖 Predictive Intelligence")
        pred_placeholder = st.empty()
        pred_placeholder.markdown(
            '<span class="pred-badge pred-calibrating">⏳ CALIBRATING</span>',
            unsafe_allow_html=True,
        )
        pred_detail = st.empty()

    # Alert banner
    alert_placeholder = st.empty()

    # Alert History
    st.markdown("#### 📋 Alert History")
    history_placeholder = st.empty()
    history_placeholder.caption("No alerts recorded yet.")

# Footer
footer_placeholder = st.empty()


# ─── TAB 2: OPERATIONS INTELLIGENCE ────────────────────────────
with tab_intel:
    st.markdown("#### 🏛️ Railway Operations Intelligence")
    st.caption("Command center analytics — threat patterns, risk trends, and resource allocation insights")

    intel_summary = st.empty()
    intel_c1, intel_c2 = st.columns(2)
    with intel_c1:
        st.markdown("##### Threat Severity Distribution")
        pie_placeholder = st.empty()
        pie_placeholder.caption("Collecting data...")
    with intel_c2:
        st.markdown("##### Risk Score Trend")
        trend_placeholder = st.empty()
        trend_placeholder.caption("Collecting data...")

    st.markdown("##### Incident Classification Breakdown")
    freq_placeholder = st.empty()
    freq_placeholder.caption("Collecting data...")


# ─── TAB 3: RDSO EVIDENCE ────────────────────────────────
with tab_forensics:
    st.markdown("#### 🏛️ RDSO-Compliant Evidence Chain")
    st.caption("Tamper-proof incident reports with SHA-256 integrity hashing — designed for legal proceedings and railway safety audits")
    forensics_summary = st.empty()
    forensics_table = st.empty()
    forensics_table.caption("No evidence generated yet. Initiate system to begin auto-capturing incident reports.")


# ─── TAB 4: INFRASTRUCTURE ZONES ───────────────────────────
with tab_zones:
    st.markdown("#### 🛡️ Critical Infrastructure Protection Zones")
    st.caption("GPS-based zone classification for bridges, tunnels, and defence corridor stretches")

    zone_map_placeholder = st.empty()
    zone_detail_placeholder = st.empty()

    # Show zone definitions table
    st.markdown("##### Infrastructure Security Classification")
    zone_data = geo_zones.get_zone_map_data()
    zone_rows = []
    for z in zone_data["zones"]:
        zone_rows.append({
            "ID": z["id"],
            "Zone": f'{z["icon"]} {z["name"]}',
            "Clearance": z.get("clearance", "General"),
            "KM Range": f'{z["km_start"]} — {z["km_end"]}',
            "Risk Bonus": f'+{z["risk_bonus"]}',
            "Description": z["description"],
        })
    st.dataframe(pd.DataFrame(zone_rows), use_container_width=True, hide_index=True)

    st.markdown("##### 🏗️ Track Section Maintenance")
    sections = maintenance.get_all_sections_status()
    sec_cols = st.columns(len(sections))
    for i, sec in enumerate(sections):
        with sec_cols[i]:
            status_icon = "🟢" if sec["active"] else "⚪"
            st.markdown(f"**{sec['section']}**")
            st.caption(f"{status_icon} {sec['task']} · {sec['team']}")


# ═══════════════════════════════════════════════════════════════════
#                       EXECUTION LOOP
# ═══════════════════════════════════════════════════════════════════

if 'stream_index' not in st.session_state:
    st.session_state['stream_index'] = 0

if run_system:
    status_indicator.markdown(
        '<div style="text-align:center"><span class="status-badge status-online">🟢 ONLINE</span></div>',
        unsafe_allow_html=True,
    )

    start_time = time.time()
    cap = None

    if data_source == "Forensic Analysis (Upload Video)" and video_file_path:
        cap = cv2.VideoCapture(video_file_path)
    elif data_source != "Forensic Analysis (Upload Video)" and use_webcam:
        cap = cv2.VideoCapture(0)

    chart_data = []
    frame_count = 0
    gauge_key = 0

    while run_system:
        # ── A. Get Vibration Data ──
        vib_level = 0.0

        if data_source == "Real-Time":
            vib_level = logic.get_real_vibration()
        elif data_source == "Forensic Analysis (Upload Video)":
            vib_level = audio_levels[frame_count] if frame_count < len(audio_levels) else 0.0
        else:  # Simulation
            if df_csv is not None and not df_csv.empty:
                idx = st.session_state['stream_index'] % len(df_csv)
                row = df_csv.iloc[idx].values
                base = np.mean(np.abs(row))
                if sim_mode == "Normal Track":
                    vib_level = base * 0.1
                elif sim_mode == "Earthquake (High)":
                    vib_level = base + 0.6
                else:  # Sabotage
                    if np.random.random() > 0.6:
                        vib_level = base + np.random.uniform(0.5, 0.9)
                    else:
                        vib_level = base + 0.1
                st.session_state['stream_index'] += 1

        # ── B. Update Predictive Engine ──
        pred_engine.update(vib_level)

        # ── C. Get Video Frame ──
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                if data_source == "Forensic Analysis (Upload Video)":
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frame_count = 0
                    continue
                else:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # ── D. AI Fusion Pipeline ──
        annotated_frame, alert_status, color, explanation, risk_score, max_conf = \
            logic.detect_threats(frame, vib_level)

        # ── E. Update Visual Feed ──
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        # ── F. Update KPI Cards ──
        elapsed = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)
        total_alerts = alert_logger.get_total_alerts()
        current_zone = geo_zones.get_current_zone()
        prediction = pred_engine.get_prediction()

        kpi_risk.metric("⚡ Risk", f"{risk_score} / 100")
        kpi_alerts.metric("🚨 Alerts", str(total_alerts))
        kpi_uptime.metric("⏱️ Uptime", f"{mins:02d}:{secs:02d}")
        kpi_confidence.metric("🎯 Conf.", f"{max_conf:.0%}" if max_conf > 0 else "—")
        kpi_zone.metric("🗺️ Zone", f'{current_zone["icon"]} {current_zone["id"]}')
        kpi_prediction.metric("🤖 Trend", f'{prediction["icon"]} {prediction["status"][:6]}')

        # ── G. Update Risk Gauge ──
        gauge_key += 1
        gauge_placeholder.plotly_chart(
            create_risk_gauge(risk_score), use_container_width=True, key=f"gauge_{gauge_key}")

        # ── H. Update Vibration Chart ──
        chart_data.append(vib_level)
        if len(chart_data) > 80:
            chart_data.pop(0)
        chart_placeholder.plotly_chart(
            create_vibration_chart(chart_data), use_container_width=True, key=f"chart_{gauge_key}")

        # ── I. Predictive Status ──
        pred_class = prediction["status"].lower().replace("-", "")
        ttc = pred_engine.get_estimated_time_to_critical()
        pred_placeholder.markdown(
            f'<span class="pred-badge pred-{pred_class}">'
            f'{prediction["icon"]} {prediction["status"]}</span>',
            unsafe_allow_html=True,
        )
        ttc_text = f"⏱️ Est. {ttc} readings to critical" if ttc and ttc > 0 else ""
        pred_detail.caption(f'{prediction["description"]} {ttc_text}')

        # ── J. Alert Banner & Status ──
        status_map = {
            "red": ("status-critical", "🔴 CRITICAL", "🚨", "error"),
            "blue": ("status-online", "🔵 MAINTENANCE", "✅", "info"),
            "orange": ("status-warning", "🟠 WARNING", "⚠️", "warning"),
            "yellow": ("status-warning", "🟡 CAUTION", "🔧", "warning"),
            "green": ("status-online", "🟢 SECURE", "✅", "success"),
        }
        css_class, label, icon, method = status_map.get(color, status_map["green"])
        status_indicator.markdown(
            f'<div style="text-align:center"><span class="status-badge {css_class}">'
            f'{label}</span></div>', unsafe_allow_html=True)
        getattr(alert_placeholder, method)(
            f"### {icon} {alert_status}\n{explanation}", icon=icon)

        # ── K. Alert History ──
        recent = alert_logger.get_recent_alerts(15)
        if recent:
            history_html = ""
            for a in recent:
                sev_class = a["severity"].lower() if a["severity"] in \
                    ["CRITICAL", "WARNING", "CAUTION", "INFO"] else ""
                history_html += (
                    f'<div class="alert-entry {sev_class}">'
                    f'<span class="alert-time">{a["timestamp"]}</span> · '
                    f'<strong>{a["severity"]}</strong> · '
                    f'<span class="alert-text">{a["alert_type"]}</span> · '
                    f'Risk: {a["risk_score"]}'
                    f'</div>')
            history_placeholder.markdown(history_html, unsafe_allow_html=True)

        # ── L. Update Analytics (every 10 frames) ──
        if frame_count % 10 == 0 and total_alerts > 0:
            # Severity pie
            sev_dist = alert_logger.get_severity_distribution()
            if sev_dist:
                sev_colors = {"CRITICAL": "#ef4444", "WARNING": "#f59e0b",
                              "CAUTION": "#eab308", "INFO": "#3b82f6", "SAFE": "#22c55e"}
                fig_pie = go.Figure(go.Pie(
                    labels=list(sev_dist.keys()),
                    values=list(sev_dist.values()),
                    hole=0.5,
                    marker=dict(colors=[sev_colors.get(k, "#6b7b8d") for k in sev_dist.keys()]),
                    textfont=dict(color="#e5e7eb", size=11),
                ))
                fig_pie.update_layout(
                    height=250, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(font=dict(color="#8899aa", size=10)),
                    showlegend=True,
                )
                pie_placeholder.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{gauge_key}")

            # Risk trend
            trend_data = alert_logger.get_risk_trend(40)
            if trend_data:
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    y=trend_data, mode='lines+markers',
                    line=dict(color='#f59e0b', width=2, shape='spline'),
                    marker=dict(size=4, color='#f59e0b'),
                    fill='tozeroy', fillcolor='rgba(245,158,11,0.08)',
                ))
                fig_trend.update_layout(
                    height=250, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)",
                               tickfont=dict(color="#3d4d5d", size=9), zeroline=False),
                    showlegend=False,
                )
                trend_placeholder.plotly_chart(fig_trend, use_container_width=True, key=f"trend_{gauge_key}")

            # Alert frequency by type
            type_dist = alert_logger.get_alert_type_distribution()
            if type_dist:
                fig_freq = go.Figure(go.Bar(
                    x=list(type_dist.values()),
                    y=list(type_dist.keys()),
                    orientation='h',
                    marker=dict(color='#00ADB5',
                                line=dict(color='rgba(0,173,181,0.3)', width=1)),
                ))
                fig_freq.update_layout(
                    height=200, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)",
                               tickfont=dict(color="#3d4d5d", size=9)),
                    yaxis=dict(tickfont=dict(color="#8899aa", size=10)),
                    showlegend=False,
                )
                freq_placeholder.plotly_chart(fig_freq, use_container_width=True, key=f"freq_{gauge_key}")

            # Summary
            summary = alert_logger.get_analytics_summary()
            intel_summary.markdown(
                f'<div class="glass-panel">'
                f'📊 <strong>Total Alerts:</strong> {summary["total"]} · '
                f'<strong>Avg Risk:</strong> {summary["avg_risk"]} · '
                f'<strong>Peak Risk:</strong> {summary["max_risk"]} · '
                f'<strong>Critical %:</strong> {summary["critical_pct"]}% · '
                f'<strong>Most Common:</strong> {summary["most_common"]}'
                f'</div>', unsafe_allow_html=True)

        # ── M. Update Forensics (every 15 frames) ──
        if frame_count % 15 == 0:
            chain = forensics.get_evidence_chain(20)
            chain_summary = forensics.get_chain_summary()

            forensics_summary.markdown(
                f'<div class="glass-panel">'
                f'🏛️ <strong>RDSO Evidence Reports:</strong> {chain_summary.get("total", 0)} · '
                f'<strong>Critical:</strong> {chain_summary.get("critical", 0)} · '
                f'<strong>Latest:</strong> {chain_summary.get("latest_id", "—")} · '
                f'<strong>RDSO Code:</strong> {chain_summary.get("latest_rdso", "—")}'
                f'</div>', unsafe_allow_html=True)

            if chain:
                evidence_html = ""
                for r in chain[:15]:
                    is_valid, verify_msg = forensics.verify_report(r)
                    status_icon = "✅" if is_valid else "❌"
                    sev_color = {"CRITICAL": "#ef4444", "WARNING": "#f59e0b"}.get(
                        r["severity"], "#6b7b8d")
                    rdso = r.get("rdso_code", "—")
                    evidence_html += (
                        f'<div class="evidence-row">'
                        f'<span class="eid">{r["incident_id"]}</span> · '
                        f'<span style="color:#00ADB5;font-weight:600">{rdso}</span> · '
                        f'<span style="color:{sev_color};font-weight:600">{r["severity"]}</span> · '
                        f'{r["alert_type"]} · '
                        f'Risk: {r["risk_score"]} · '
                        f'{status_icon} '
                        f'<span class="hash">{r["integrity_hash"][:20]}...</span> · '
                        f'<span style="color:#506070">{r["timestamp"]}</span>'
                        f'</div>')
                forensics_table.markdown(evidence_html, unsafe_allow_html=True)

        # ── N. Update Zone Map (every 20 frames) ──
        if frame_count % 20 == 0:
            zdata = geo_zones.get_zone_map_data()
            zone_map_placeholder.markdown(create_zone_map_html(zdata), unsafe_allow_html=True)
            cz = geo_zones.get_current_zone()
            zone_type_class = {"safe": "zone-safe", "buffer": "zone-buffer",
                               "restricted": "zone-restricted"}.get(cz["type"], "zone-safe")
            zone_detail_placeholder.markdown(
                f'<div class="glass-panel">'
                f'<span class="zone-badge {zone_type_class}">{cz["icon"]} {cz["name"]}</span> · '
                f'KM: {cz["current_km"]} · '
                f'Risk Bonus: +{cz["risk_bonus"]} · '
                f'{cz["description"]}'
                f'</div>', unsafe_allow_html=True)

        # ── O. Footer ──
        ev_count = forensics.get_evidence_count()
        footer_placeholder.markdown(
            f'<div class="system-footer">'
            f'YOLOv8n + IsolationForest + FusionEngine · '
            f'Frame: {frame_count} · '
            f'Vib: {vib_level:.3f} · '
            f'Risk: {risk_score}/100 · '
            f'Zone: {current_zone["id"]} · '
            f'Alerts: {total_alerts} · '
            f'Evidence: {ev_count} · '
            f'Pred: {prediction["status"]} · '
            f'{datetime.datetime.now().strftime("%H:%M:%S")}'
            f'</div>', unsafe_allow_html=True)

        frame_count += 1
        time.sleep(0.01 if data_source == "Forensic Analysis (Upload Video)" else 0.05)

    if cap:
        cap.release()
else:
    status_indicator.markdown(
        '<div style="text-align:center"><span class="status-badge status-standby">⚪ PAUSED</span></div>',
        unsafe_allow_html=True)

    # Show static zone map when idle
    with tab_zones:
        zdata = geo_zones.get_zone_map_data()
        zone_map_placeholder.markdown(create_zone_map_html(zdata), unsafe_allow_html=True)
        cz = geo_zones.get_current_zone()
        zone_detail_placeholder.markdown(
            f'<div class="glass-panel">{cz["icon"]} {cz["name"]} · KM: {cz["current_km"]} · '
            f'Risk Bonus: +{cz["risk_bonus"]}</div>', unsafe_allow_html=True)