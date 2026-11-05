"""
pages/8_Reports.py
------------------
Multi-Format Research Reporting & Export Module for MEDANALYTIX.
Generates multi-sheet Excel workbooks, executive HTML reports, Markdown summaries, and CSVs.
"""

import streamlit as st
import pandas as pd
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header,
    check_dataset_or_warn
)
from modules.report_generator import (
    generate_multi_sheet_excel,
    generate_executive_html_report
)
from modules.data_quality import compute_column_quality_summary, calculate_data_quality_score
from modules.statistical_analysis import compute_numerical_descriptives
from modules.healthcare_analytics import analyze_amoxicillin_distribution
from modules.data_cleaning import export_dataframe_to_csv

st.set_page_config(
    page_title="Reports & Downloads | MEDANALYTIX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar()

render_page_header(
    title="Analytical Reports & Data Exports",
    subtitle="Generate publication-grade research documentation, multi-sheet workbooks, and executive summaries.",
    tag="Research Documentation Engine"
)

df, metadata = check_dataset_or_warn()

if df is not None and metadata is not None:
    # 1. Compile Live Data for Reports
    quality_summary_df = compute_column_quality_summary(df)
    quality_score, quality_grade, _ = calculate_data_quality_score(df)
    cleaning_log = st.session_state.get("cleaning_log", [])
    descriptives_df = compute_numerical_descriptives(df)
    
    amox_df = None
    if metadata.get("is_amoxicillin_research"):
        amox_counts, _ = analyze_amoxicillin_distribution(df)
        amox_df = amox_counts

    st.markdown("### 📥 Download Formats")

    col1, col2, col3 = st.columns(3, gap="medium")

    # --- Format 1: Multi-Sheet Excel ---
    with col1:
        st.markdown("""
        <div class="med-card" style="text-align:center;">
            <div style="font-size:2.4rem; margin-bottom:8px;">📊</div>
            <h4 style="color:#ffffff; margin:0 0 6px 0;">Executive Excel Workbook</h4>
            <p style="font-size:0.8rem; color:#94a3b8; min-height:48px;">
                Includes Overview, Cleaned Data, Quality Audit, Transformation Log, and AMR Profiles.
            </p>
        """, unsafe_allow_html=True)
        excel_bytes = generate_multi_sheet_excel(
            df=df,
            metadata=metadata,
            quality_summary_df=quality_summary_df,
            cleaning_log=cleaning_log,
            descriptives_df=descriptives_df,
            amox_df=amox_df
        )
        st.download_button(
            label="💾 Download .XLSX Workbook",
            data=excel_bytes,
            file_name="medanalytix_research_workbook.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Format 2: Printable HTML / PDF ---
    with col2:
        st.markdown("""
        <div class="med-card" style="text-align:center;">
            <div style="font-size:2.4rem; margin-bottom:8px;">📄</div>
            <h4 style="color:#ffffff; margin:0 0 6px 0;">Printable HTML / PDF Report</h4>
            <p style="font-size:0.8rem; color:#94a3b8; min-height:48px;">
                Styled executive report ready for browser review, thesis attachment, or print to PDF.
            </p>
        """, unsafe_allow_html=True)
        html_report = generate_executive_html_report(
            df=df,
            metadata=metadata,
            quality_summary_df=quality_summary_df,
            cleaning_log=cleaning_log,
            descriptives_df=descriptives_df,
            quality_score=quality_score,
            quality_grade=quality_grade,
            amox_df=amox_df
        )
        st.download_button(
            label="🌐 Download HTML Report",
            data=html_report.encode("utf-8"),
            file_name="medanalytix_executive_report.html",
            mime="text/html",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Format 3: Cleaned CSV ---
    with col3:
        st.markdown("""
        <div class="med-card" style="text-align:center;">
            <div style="font-size:2.4rem; margin-bottom:8px;">📁</div>
            <h4 style="color:#ffffff; margin:0 0 6px 0;">Cleaned Dataset (CSV)</h4>
            <p style="font-size:0.8rem; color:#94a3b8; min-height:48px;">
                Raw data matrix reflecting all applied cleaning and standardization transformations.
            </p>
        """, unsafe_allow_html=True)
        csv_bytes = export_dataframe_to_csv(df)
        st.download_button(
            label="💾 Download Cleaned CSV",
            data=csv_bytes,
            file_name="medanalytix_cleaned_dataset.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Live Report Preview
    st.markdown("### 👁️ Live Report Preview")
    with st.expander("📄 Click to Preview Full HTML Executive Report Inline", expanded=True):
        st.components.v1.html(html_report, height=650, scrolling=True)

    # Markdown Summary Preview
    with st.expander("📋 View Markdown Research Summary", expanded=False):
        md_text = f"""
# MEDANALYTIX Research Summary Report
- **Source File:** `{metadata.get('filename')}`
- **Total Records:** `{metadata.get('rows'):,}`
- **Total Variables:** `{metadata.get('columns')}`
- **Quality Index:** `{quality_score}/100` ({quality_grade})
- **Transformations Logged:** `{len(cleaning_log)} operations`
- **Clinical Governance:** De-identified local computation; zero remote exfiltration.
        """
        st.markdown(md_text)
        st.download_button(
            label="📥 Download Markdown Summary (.md)",
            data=md_text.encode("utf-8"),
            file_name="medanalytix_summary.md",
            mime="text/markdown"
        )

