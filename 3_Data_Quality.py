"""
pages/3_Data_Quality.py
-----------------------
Automated Data Quality Audit Module for MEDANALYTIX.
Profiles completeness, uniqueness, consistency, outliers, and patient ID integrity.
"""

import streamlit as st
import pandas as pd
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header,
    check_dataset_or_warn
)
from modules.data_quality import (
    compute_column_quality_summary,
    calculate_data_quality_score,
    detect_outliers_iqr,
    audit_identifier_columns
)
from modules.eda_engine import plot_missing_values_matrix

st.set_page_config(
    page_title="Data Quality Audit | MEDANALYTIX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar()

render_page_header(
    title="Data Quality Audit",
    subtitle="Comprehensive automated health data profiling: completeness, uniqueness, outliers, and schema consistency.",
    tag="Data Governance & Verification"
)

df, metadata = check_dataset_or_warn()

if df is not None and metadata is not None:
    # 1. Quality Scoring
    quality_score, grade, breakdown = calculate_data_quality_score(df)

    # 2. Score Summary Banner
    st.markdown(f"""
    <div class="med-card" style="border-left: 4px solid #00f2fe;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
            <div>
                <span class="badge-cyan">Composite Quality Assessment</span>
                <h2 style="color:#ffffff; margin: 6px 0 2px 0;">Quality Index: <span style="color:#00f2fe;">{quality_score} / 100</span></h2>
                <div style="color:#94a3b8; font-size:0.95rem;">Audit Classification: <b>{grade}</b></div>
            </div>
            <div style="display:flex; gap:20px;">
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; text-transform:uppercase; color:#94a3b8;">Completeness Score</div>
                    <div style="font-size:1.4rem; font-weight:700; color:#10b981;">{breakdown['completeness']} / 40</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; text-transform:uppercase; color:#94a3b8;">Uniqueness Score</div>
                    <div style="font-size:1.4rem; font-weight:700; color:#38bdf8;">{breakdown['uniqueness']} / 30</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; text-transform:uppercase; color:#94a3b8;">Consistency Score</div>
                    <div style="font-size:1.4rem; font-weight:700; color:#8b5cf6;">{breakdown['consistency']} / 30</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Flaw Counters Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Missing Data Cells", f"{breakdown['total_missing']:,}", help="Total NaN or null fields across all features.")
    with col2:
        st.metric("Exact Duplicate Rows", f"{breakdown['total_duplicates']:,}", help="Rows with identical values across all features.")
    with col3:
        st.metric("Statistical Outliers (IQR)", f"{breakdown['total_outliers']:,}", help="Values beyond 1.5x Interquartile Range.")
    with col4:
        st.metric("Whitespace Flaws", f"{breakdown['total_whitespace_flaws']:,}", help="Strings containing leading or trailing whitespaces.")

    st.markdown("---")

    # 4. Column-Level Quality Audit Table
    st.markdown("### 📋 Column-Level Quality Matrix")
    col_summary = compute_column_quality_summary(df)
    st.dataframe(col_summary, use_container_width=True)

    # 5. Missing Values Visualization
    st.markdown("### 📉 Feature Missingness Breakdown")
    fig_missing = plot_missing_values_matrix(df)
    st.plotly_chart(fig_missing, use_container_width=True)

    # 6. Outlier Analysis & Identifiers Tabbed Section
    tab_outliers, tab_ids, tab_dups = st.tabs(["📊 Outlier Details (IQR)", "🆔 Identifier Auditing", "👥 Duplicate Records"])

    with tab_outliers:
        outlier_data = detect_outliers_iqr(df)
        if outlier_data:
            st.markdown("#### Numerical Outlier Detection (Tukey's Rule)")
            outlier_rows = []
            for col_name, stats in outlier_data.items():
                outlier_rows.append({
                    "Feature": col_name,
                    "Q1 (25%)": stats["q25"],
                    "Median (50%)": stats["median"],
                    "Q3 (75%)": stats["q75"],
                    "IQR": stats["iqr"],
                    "Lower Bound": stats["lower_bound"],
                    "Upper Bound": stats["upper_bound"],
                    "Outlier Count": stats["outlier_count"],
                    "Outlier (%)": f"{stats['outlier_percentage']}%"
                })
            st.dataframe(pd.DataFrame(outlier_rows), use_container_width=True)
        else:
            st.info("No numerical features available or insufficient data for IQR analysis.")

    with tab_ids:
        id_audit = audit_identifier_columns(df)
        if id_audit:
            st.markdown("#### Primary Identifier Column Auditing")
            for id_col, id_stats in id_audit.items():
                st.markdown(f"""
                <div class="med-card">
                    <div class="med-card-header">
                        <div class="med-card-title">Identifier: <code>{id_col}</code></div>
                        <span class="{'badge-success' if id_stats['is_unique_primary_key'] else 'badge-warning'}">
                            {'Unique Primary Key' if id_stats['is_unique_primary_key'] else 'Repeated Identifiers Detected'}
                        </span>
                    </div>
                    <div style="font-size:0.9rem; color:#cbd5e1;">
                        Total Records: <b>{id_stats['total_records']:,}</b> &bull; 
                        Unique IDs: <b>{id_stats['unique_ids']:,}</b> &bull; 
                        Repeated Entries: <b style="color:{'#f59e0b' if id_stats['repeated_ids_count']>0 else '#10b981'};">{id_stats['repeated_ids_count']:,}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No explicit ID or Patient identifier columns detected in this dataset.")

    with tab_dups:
        dups_df = df[df.duplicated(keep=False)]
        if not dups_df.empty:
            st.warning(f"⚠️ Found {len(dups_df)} records belonging to duplicate groups.")
            st.dataframe(dups_df.head(20), use_container_width=True)
        else:
            st.success("✅ Zero duplicate rows detected in the active dataset!")

    st.markdown("""
    <div class="info-banner">
        💡 <b>DATA GOVERNANCE POLICY:</b> MEDANALYTIX never modifies or drops observations automatically during an audit. To remediate identified anomalies, proceed to the <b>Data Cleaning Module</b>.
    </div>
    """, unsafe_allow_html=True)

