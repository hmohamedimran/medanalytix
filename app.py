"""
app.py
------
MEDANALYTIX - Healthcare Data Intelligence Platform
Main application entry point.
"""

import streamlit as st
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header,
    check_dataset_or_warn
)
from modules.data_quality import calculate_data_quality_score
from modules.healthcare_analytics import analyze_amoxicillin_distribution
from modules.eda_engine import plot_numerical_distribution, plot_categorical_distribution

# 1. Page Configuration
st.set_page_config(
    page_title="MEDANALYTIX | Healthcare Data Intelligence Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Stylesheet and Sidebar
inject_custom_css()
render_sidebar()

# 3. Hero Banner
render_page_header(
    title="MEDANALYTIX",
    subtitle="Healthcare Data Intelligence Platform &bull; Advanced Clinical Analytics & Data Quality Audit",
    tag="MCA Healthcare Analytics Platform"
)

# 4. Check Dataset Status
df, metadata = check_dataset_or_warn()

if df is not None and metadata is not None:
    quality_score, grade, breakdown = calculate_data_quality_score(df)
    
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Records</div>
            <div class="kpi-value">{metadata['rows']:,}</div>
            <div class="kpi-subtext">Isolates / Patient observations</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Total Variables</div>
            <div class="kpi-value">{metadata['columns']}</div>
            <div class="kpi-subtext">{len(metadata['numerical_columns'])} Num &bull; {len(metadata['categorical_columns'])} Cat</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Data Quality Score</div>
            <div class="kpi-value" style="color:#00f2fe;">{quality_score}%</div>
            <div class="kpi-subtext">{grade}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Missing Cells</div>
            <div class="kpi-value" style="color:{'#10b981' if metadata['total_missing']==0 else '#f59e0b'};">
                {metadata['total_missing']:,}
            </div>
            <div class="kpi-subtext">{metadata['missing_percentage']}% of total data matrix</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Duplicate Rows</div>
            <div class="kpi-value" style="color:{'#10b981' if metadata['duplicate_rows']==0 else '#f43f5e'};">
                {metadata['duplicate_rows']}
            </div>
            <div class="kpi-subtext">{metadata['duplicate_percentage']}% duplicate frequency</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Memory Footprint</div>
            <div class="kpi-value" style="font-size:1.6rem; padding-top:4px;">{metadata['memory_usage']}</div>
            <div class="kpi-subtext">Active RAM allocation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 1], gap="medium")

    with col_left:
        st.markdown("""
        <div class="med-card">
            <div class="med-card-header">
                <div class="med-card-title">🔍 Quick Data Preview</div>
                <span class="badge-cyan">First 10 Observations</span>
            </div>
        """, unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        recent_ops = st.session_state.get("recent_operations", [])
        cleaning_log = st.session_state.get("cleaning_log", [])
        
        st.markdown("""
        <div class="med-card">
            <div class="med-card-header">
                <div class="med-card-title">⚡ Session Operational Audit Trail</div>
                <span class="badge-violet">Live History</span>
            </div>
        """, unsafe_allow_html=True)
        
        if recent_ops or cleaning_log:
            for op in reversed(recent_ops[-4:]):
                st.markdown(f"<div style='font-size:0.85rem; color:#cbd5e1; margin-bottom:6px;'>&bull; {op}</div>", unsafe_allow_html=True)
            for c in reversed(cleaning_log[-3:]):
                st.markdown(f"<div style='font-size:0.85rem; color:#00f2fe; margin-bottom:6px;'>&bull; <b>{c['action']}</b>: {c['details']}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#64748b; font-size:0.85rem;'>No active data operations recorded yet.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        if metadata.get("is_amoxicillin_research"):
            st.markdown("""
            <div class="med-card">
                <div class="med-card-header">
                    <div class="med-card-title">🔬 Amoxicillin Phenotype Overview</div>
                    <span class="badge-violet">Research Target</span>
                </div>
            """, unsafe_allow_html=True)
            amox_counts, amox_fig = analyze_amoxicillin_distribution(df)
            if amox_fig:
                st.plotly_chart(amox_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="med-card">
                <div class="med-card-header">
                    <div class="med-card-title">📈 Feature Distribution Preview</div>
                    <span class="badge-cyan">Univariate</span>
                </div>
            """, unsafe_allow_html=True)
            if metadata["numerical_columns"]:
                fig_preview = plot_numerical_distribution(df, metadata["numerical_columns"][0])
                st.plotly_chart(fig_preview, use_container_width=True)
            elif metadata["categorical_columns"]:
                fig_preview = plot_categorical_distribution(df, metadata["categorical_columns"][0])
                st.plotly_chart(fig_preview, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="clinical-disclaimer">
        <b>CLINICAL RESEARCH GOVERNANCE NOTICE:</b> All analytical telemetry and predictive markers displayed are computed strictly from retrospective experimental data. This platform is engineered for healthcare informatics research and hypothesis generation under MCA methodology, and does not constitute medical advice or automated clinical prescription.
    </div>
    """, unsafe_allow_html=True)

