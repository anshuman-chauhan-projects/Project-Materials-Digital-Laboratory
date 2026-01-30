import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import tempfile
import os

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Materials Digital Lab",
    page_icon="🧪",
    layout="wide"
)

# ======================================================
# CUSTOM CSS — COOL WEBSITE LOOK
# ======================================================
st.markdown("""
<style>
body {
    background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #EAF6F6;
}
p, label, div {
    color: #EAF6F6;
}
.card {
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    margin-bottom: 20px;
}
.badge-safe {
    background-color: #00ff9c;
    color: black;
    padding: 8px 14px;
    border-radius: 20px;
    font-weight: bold;
}
.badge-fail {
    background-color: #ff4b4b;
    color: white;
    padding: 8px 14px;
    border-radius: 20px;
    font-weight: bold;
}
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #141e30, #243b55);
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================
st.markdown("""
<div class="card">
<h1>🧪 Materials Digital Laboratory</h1>
<p>Intelligent Tensile • Fatigue • Failure • Processing Platform</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR — MACHINE PANEL
# ======================================================
st.sidebar.title("🔬 Machine Control Panel")

material = st.sidebar.text_input("Material", "Structural Steel")
operator = st.sidebar.text_input("Operator", "Lab Engineer")
standard = st.sidebar.selectbox("Test Standard", ["ASTM E8 (0.2% Offset)", "ISO 6892"])

st.sidebar.markdown("---")
st.sidebar.caption("Digital UTM Interface")

# ======================================================
# FILE UPLOAD
# ======================================================
st.markdown("<div class='card'><h3>📥 Upload Experimental Data</h3></div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload CSV (strain, stress)", type=["csv"])

if uploaded_file is None:
    st.stop()

data = pd.read_csv(uploaded_file)
strain = data["strain"]
stress = data["stress"]

# ======================================================
# ASTM 0.2% OFFSET CALCULATION
# ======================================================
E = np.polyfit(strain[:5], stress[:5], 1)[0]
offset_line = E * (strain + 0.002)
yield_index = np.abs(stress - offset_line).idxmin()

yield_stress = stress.iloc[yield_index]
uts_index = np.argmax(stress)
uts_stress = stress.iloc[uts_index]
fracture_stress = stress.iloc[-1]
fracture_strain = strain.iloc[-1]

# ======================================================
# TABS
# ======================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Tensile", "🔁 Fatigue", "⚠️ Failure & Heat", "📄 Report"])

# ======================================================
# TAB 1 — TENSILE
# ======================================================
with tab1:
    st.markdown("<div class='card'><h3>Stress–Strain Curve (ASTM)</h3></div>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strain, y=stress, mode="lines", name="Stress–Strain"))
    fig.add_trace(go.Scatter(x=strain, y=offset_line, mode="lines", name="0.2% Offset", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=[strain.iloc[yield_index]], y=[yield_stress], mode="markers", name="Yield"))
    fig.add_trace(go.Scatter(x=[strain.iloc[uts_index]], y=[uts_stress], mode="markers", name="UTS"))
    fig.add_trace(go.Scatter(x=[strain.iloc[-1]], y=[fracture_stress], mode="markers", name="Fracture"))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Strain",
        yaxis_title="Stress (MPa)"
    )

    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Young’s Modulus (MPa)", f"{E:.2f}")
    c2.metric("Yield Stress", f"{yield_stress:.2f}")
    c3.metric("UTS", f"{uts_stress:.2f}")
    c4.metric("Fracture Stress", f"{fracture_stress:.2f}")

# ======================================================
# TAB 2 — FATIGUE
# ======================================================
with tab2:
    st.markdown("<div class='card'><h3>Fatigue Life (S–N)</h3></div>", unsafe_allow_html=True)

    stress_levels = np.array([uts_stress*0.9, uts_stress*0.75, uts_stress*0.6])
    cycles = np.array([1e4, 1e5, 1e6])

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=stress_levels, y=cycles, mode="lines+markers"))
    fig2.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Stress Amplitude (MPa)",
        yaxis_title="Cycles",
        yaxis_type="log"
    )

    st.plotly_chart(fig2, use_container_width=True)

    working_stress = st.slider("Working Stress (MPa)", 50, int(uts_stress), 200)
    fatigue_life = (1000 / working_stress)**3 * 1e6

    if fatigue_life >= 1e6:
        st.markdown("<span class='badge-safe'>SAFE DESIGN</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge-fail'>FAILURE LIKELY</span>", unsafe_allow_html=True)

# ======================================================
# TAB 3 — FAILURE & HEAT
# ======================================================
with tab3:
    st.markdown("<div class='card'><h3>Failure Intelligence</h3></div>", unsafe_allow_html=True)

    stress_drop = uts_stress - fracture_stress

    if fracture_strain > 0.25:
        failure = "Ductile Fracture (Cup & Cone)"
        heat = "Normalizing / Annealing"
    elif stress_drop > 0.5 * uts_stress:
        failure = "Brittle Cleavage"
        heat = "Annealing"
    else:
        failure = "Low-Cycle Fatigue"
        heat = "Quench & Temper"

    st.info(f"🧠 Failure Mode: **{failure}**")
    st.success(f"🔥 Recommended Heat Treatment: **{heat}**")

# ======================================================
# TAB 4 — REPORT
# ======================================================
with tab4:
    st.markdown("<div class='card'><h3>Auto Lab Report</h3></div>", unsafe_allow_html=True)

    if st.button("Generate PDF Report"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            path = tmp.name

        c = canvas.Canvas(path, pagesize=A4)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "Materials Digital Lab Report")

        c.setFont("Helvetica", 11)
        c.drawString(50, 760, f"Material: {material}")
        c.drawString(50, 740, f"Operator: {operator}")
        c.drawString(50, 720, f"Standard: {standard}")
        c.drawString(50, 700, f"Date: {datetime.now().strftime('%d-%m-%Y')}")

        c.drawString(50, 660, f"Yield Stress: {yield_stress:.2f} MPa")
        c.drawString(50, 640, f"UTS: {uts_stress:.2f} MPa")
        c.drawString(50, 620, f"Failure Mode: {failure}")
        c.drawString(50, 600, f"Heat Treatment: {heat}")

        c.save()

        with open(path, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name="Materials_Lab_Report.pdf")

        os.remove(path)

# ======================================================
# FOOTER
# ======================================================
st.markdown("<p style='text-align:center;'>🚀 Final-Year Project • Materials Digital Lab</p>", unsafe_allow_html=True)
