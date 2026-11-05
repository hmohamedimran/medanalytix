"""
pages/9_About.py
----------------
About the Platform, Research Methodology, and Privacy Governance for MEDANALYTIX.
"""

import streamlit as st
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header
)

st.set_page_config(
    page_title="About Project | MEDANALYTIX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar()

render_page_header(
    title="About MEDANALYTIX",
    subtitle="Healthcare Data Intelligence Platform &bull; Architectural Blueprint & Research Governance.",
    tag="System Information & Governance"
)

# Main Grid
col_left, col_right = st.columns([1.2, 0.8], gap="medium")

with col_left:
    st.markdown("""
    <div class="med-card">
        <div class="med-card-header">
            <div class="med-card-title">🎯 Project Vision & Academic Scope</div>
            <span class="badge-cyan">MCA Research Project</span>
        </div>
        <p style="color:#cbd5e1; font-size:0.95rem; line-height:1.6;">
            <b>MEDANALYTIX</b> is a dedicated healthcare analytics and intelligence platform engineered to bridge clinical microbiology, laboratory information systems (LIS), and automated data science.
        </p>
        <p style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
            Developed as part of an advanced <b>MCA Healthcare Analytics Research Project</b> titled:<br>
            <span style="color:#00f2fe; font-weight:600;">"Analysis and Prediction of Amoxicillin Resistance in Bacterial Isolates Using Machine Learning"</span>
        </p>
        <p style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
            The platform delivers commercial SaaS-grade visual telemetry, rigorous automated data quality audits, non-destructive cleaning, and biostatistical hypothesis testing while maintaining strict compliance with clinical microbiology standards (CLSI / EUCAST).
        </p>
    </div>

    <div class="med-card">
        <div class="med-card-header">
            <div class="med-card-title">🔒 Data Privacy, Safety & Ethical Protocol</div>
            <span class="badge-success">Zero Remote Exfiltration</span>
        </div>
        <ul style="color:#cbd5e1; font-size:0.9rem; line-height:1.7; padding-left:20px;">
            <li><b>100% Local Ingestion:</b> Datasets uploaded into MEDANALYTIX are evaluated exclusively inside the active running runtime memory. No records are transmitted to third-party APIs, remote AI wrappers, or cloud storage.</li>
            <li><b>De-Identification First:</b> In accordance with healthcare data protection guidelines (HIPAA, GDPR, DPDP), users should ensure that datasets are de-identified prior to analysis.</li>
            <li><b>Ephemeral Session Memory:</b> Patient records and operational logs are stored in runtime session state and purged upon session termination.</li>
            <li><b>Audit Traceability:</b> Every cleaning transformation maintains an immutable before-and-after audit log to guarantee scientific reproducibility.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="med-card">
        <div class="med-card-header">
            <div class="med-card-title">⚙️ Technology Stack</div>
            <span class="badge-violet">Production Framework</span>
        </div>
        <table style="width:100%; font-size:0.85rem; color:#cbd5e1;">
            <tr><td style="padding:6px 0;"><b>Frontend & Core</b></td><td style="color:#00f2fe;">Python 3.10+ / Streamlit</td></tr>
            <tr><td style="padding:6px 0;"><b>Data Engine</b></td><td style="color:#00f2fe;">Pandas / NumPy</td></tr>
            <tr><td style="padding:6px 0;"><b>Visual Telemetry</b></td><td style="color:#00f2fe;">Plotly / Matplotlib / Seaborn</td></tr>
            <tr><td style="padding:6px 0;"><b>Statistical Engine</b></td><td style="color:#00f2fe;">SciPy (Chi2, ANOVA, Cramér's V)</td></tr>
            <tr><td style="padding:6px 0;"><b>ML Pipeline</b></td><td style="color:#00f2fe;">Scikit-learn (Preprocessing / Audit)</td></tr>
            <tr><td style="padding:6px 0;"><b>Workbook Export</b></td><td style="color:#00f2fe;">OpenPyXL</td></tr>
            <tr><td style="padding:6px 0;"><b>Design System</b></td><td style="color:#8b5cf6;">Obsidian Black + Neon Cyan + Violet</td></tr>
        </table>
    </div>

    <div class="med-card">
        <div class="med-card-header">
            <div class="med-card-title">📑 Research Architecture</div>
            <span class="badge-cyan">Pipeline Modules</span>
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; line-height:1.7;">
            &bull; <b>Module 1:</b> Data Quality Audit & Completeness<br>
            &bull; <b>Module 2:</b> User-Controlled Remediation & Cleaning<br>
            &bull; <b>Module 3:</b> Exploratory Data Analysis & Bivariate Telemetry<br>
            &bull; <b>Module 4:</b> Biostatistical Hypothesis Testing (χ², ANOVA)<br>
            &bull; <b>Module 5:</b> Antimicrobial Resistance (AMR) Clinical Intelligence<br>
            &bull; <b>Module 6:</b> Multi-Sheet Executive Reporting Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

# Governance Disclaimer
st.markdown("""
<div class="clinical-disclaimer">
    <b>MANDATORY CLINICAL RESEARCH DISCLAIMER:</b><br>
    MEDANALYTIX is an academic and clinical research intelligence software platform designed to assist researchers, biostatisticians, and healthcare data professionals.
    The analytical calculations, statistical models, and visualizations generated by this platform are based exclusively on retrospective research datasets.
    This platform does not provide automated clinical diagnosis, does not issue medical prescriptions, and should never be used as a substitute for licensed clinical judgment.
</div>
""", unsafe_allow_html=True)

