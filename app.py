import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Materials Digital Laboratory",
    page_icon="🧪",
    layout="wide"
)

# ======================================================
# CSS — INDUSTRIAL DARK UI
# ======================================================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 20px;
}
.safe {
    color:#00ff9c;
    font-weight:bold;
}
.fail {
    color:#ff4b4b;
    font-weight:bold;
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
# SIDEBAR
# ======================================================
st.sidebar.title("🔬 Machine Control Panel")
material = st.sidebar.text_input("Material", "Structural Steel")
operator = st.sidebar.text_input("Operator", "Lab Engineer")
standard = st.sidebar.selectbox("Test Standard", ["ASTM E8 (0.2% Offset)", "ISO 6892"])

# ======================================================
# FILE UPLOAD
# ======================================================
st.markdown("<div class='card'><h3>📥 Upload Experimental Data</h3></div>", unsafe_allow_html=True)
file = st.file_uploader("Upload CSV (strain, stress)", type=["csv"])
if file is None:
    st.stop()

df = pd.read_csv(file)
strain = df["strain"]
stress = df["stress"]

# ======================================================
# ASTM 0.2% OFFSET
# ======================================================
E = np.polyfit(strain[:5], stress[:5], 1)[0]
offset = E * (strain + 0.002)
yield_idx = np.abs(stress - offset).idxmin()

yield_stress = stress[yield_idx]
uts_stress = stress.max()
fracture_stress = stress.iloc[-1]
fracture_strain = strain.iloc[-1]

# ======================================================
# TABS
# ======================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Tensile", "🔁 Fatigue & Design", "🔥 Heat & Failure", "📄 Report"]
)

# ======================================================
# TAB 1 — TENSILE
# ======================================================
with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strain, y=stress, name="Stress–Strain"))
    fig.add_trace(go.Scatter(x=strain, y=offset, name="0.2% Offset", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=[strain[yield_idx]], y=[yield_stress], mode="markers", name="Yield"))
    fig.add_trace(go.Scatter(x=[strain[stress.idxmax()]], y=[uts_stress], mode="markers", name="UTS"))

    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 — FATIGUE & DESIGN
# ======================================================
with tab2:
    st.markdown("<div class='card'><h3>Fatigue Design Philosophy</h3></div>", unsafe_allow_html=True)

    method = st.selectbox("Design Criterion", ["Goodman", "Soderberg", "Gerber"])
    fos = st.slider("Factor of Safety", 1.0, 3.0, 1.5, 0.1)
    working_stress = st.slider("Working Stress (MPa)", 50, int(uts_stress), 200)

    endurance = 0.5 * uts_stress

    if method == "Goodman":
        allowable = endurance * (1 - working_stress / uts_stress)
    elif method == "Soderberg":
        allowable = endurance * (1 - working_stress / yield_stress)
    else:
        allowable = endurance * (1 - (working_stress / uts_stress)**2)

    safe = allowable / fos

    if working_stress < safe:
        st.markdown("<p class='safe'>SAFE DESIGN ✔</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p class='fail'>FAILURE LIKELY ✖</p>", unsafe_allow_html=True)

# ======================================================
# TAB 3 — HEAT & FAILURE
# ======================================================
with tab3:
    st.markdown("<div class='card'><h3>Heat Treatment Simulator</h3></div>", unsafe_allow_html=True)

    treatment = st.selectbox(
        "Heat Treatment",
        ["Annealed", "Normalized", "Quenched", "Tempered"]
    )

    if treatment == "Annealed":
        ys_mod = yield_stress * 0.8
        ductility = "High"
        micro = "Ferrite + Pearlite"
    elif treatment == "Normalized":
        ys_mod = yield_stress * 1.0
        ductility = "Medium"
        micro = "Fine Pearlite"
    elif treatment == "Quenched":
        ys_mod = yield_stress * 1.4
        ductility = "Low"
        micro = "Martensite"
    else:
        ys_mod = yield_stress * 1.2
        ductility = "Medium"
        micro = "Tempered Martensite / Bainite"

    st.info(f"Modified Yield Strength: **{ys_mod:.1f} MPa**")
    st.info(f"Ductility Level: **{ductility}**")
    st.success(f"Predicted Microstructure: **{micro}**")

    st.caption("⚠️ Conceptual prediction for academic purposes")

    # AI Verdict
    verdict = (
        "The material exhibits ductile behavior suitable for cyclic loading."
        if fracture_strain > 0.2
        else "Material shows brittle tendency, use with caution."
    )
    st.markdown("### 🤖 AI Verdict")
    st.write(verdict)

    # Chatbot
    st.markdown("### 💬 Ask the Material")
    q = st.text_input("Ask a question")

    if q:
        if "bridge" in q.lower():
            st.write("Safe for bridges with Factor of Safety > 2 and fatigue control.")
        elif "fatigue" in q.lower():
            st.write("Fatigue life depends strongly on stress amplitude.")
        else:
            st.write("Material suitable for general structural applications.")

# ======================================================
# TAB 4 — REPORT
# ======================================================
with tab4:
    st.markdown("<div class='card'><h3>Auto Lab Report</h3></div>", unsafe_allow_html=True)

    st.markdown(f"""
**Aim:** Tensile & fatigue characterization  
**Material:** {material}  
**Standard:** {standard}  

**Results**
- Yield Stress: {yield_stress:.2f} MPa  
- UTS: {uts_stress:.2f} MPa  
- Failure Strain: {fracture_strain:.2f}  

**Conclusion**
Material behavior is suitable for engineering design within fatigue limits.
""")

    st.success("Report ready for university submission")

# ======================================================
# FOOTER
# ======================================================
st.markdown("""
<p style='text-align:center;opacity:0.7;'>
🚀 Final Year Project — Materials Digital Lab<br>
Intelligent Mechanical Characterization Platform
</p>
""", unsafe_allow_html=True)
