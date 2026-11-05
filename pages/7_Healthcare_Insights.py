"""
pages/7_Healthcare_Insights.py
------------------------------
Specialized Antimicrobial Resistance (AMR) Clinical Analytics for MEDANALYTIX.
Directly implements research requirements for:
"Analysis and Prediction of Amoxicillin Resistance in Bacterial Isolates Using Machine Learning"
"""

import streamlit as st
import pandas as pd
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header,
    check_dataset_or_warn
)
from modules.healthcare_analytics import (
    audit_research_columns_presence,
    analyze_amoxicillin_distribution,
    analyze_resistance_by_age_group,
    analyze_resistance_by_specimen,
    analyze_resistance_genes_distribution,
    analyze_cross_resistance_panel,
    analyze_amr_hierarchical_sunburst
)

st.set_page_config(
    page_title="Healthcare Insights | MEDANALYTIX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar()

render_page_header(
    title="Antimicrobial Resistance (AMR) Analytics",
    subtitle="Specialized clinical intelligence for bacterial isolate susceptibility and molecular resistance profiles.",
    tag="CLSI / EUCAST Protocol Alignment"
)

df, metadata = check_dataset_or_warn()

if df is not None and metadata is not None:
    # 1. Audit Research Column Presence
    audit_col_res = audit_research_columns_presence(df)

    # Research Header Box
    st.markdown("""
    <div class="med-card" style="border-left: 4px solid #8b5cf6;">
        <span class="badge-violet">MCA Healthcare Analytics Core Research Protocol</span>
        <h3 style="color:#ffffff; margin: 8px 0 4px 0;">Analysis and Prediction of Amoxicillin Resistance in Bacterial Isolates</h3>
        <p style="color:#94a3b8; font-size:0.88rem; margin:0;">
            Standardized evaluation of microbial isolates, biological specimens, diagnostic methodologies, and molecular beta-lactamase genes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Column Detection Status Bar
    with st.expander(f"🔬 Research Schema Audit ({audit_col_res['available_count']} / {audit_col_res['total_expected']} Standard Markers Detected)", expanded=not audit_col_res["has_target"]):
        cols_detected = audit_col_res["detected"]
        c_grid = st.columns(4)
        for i, (col_name, is_present) in enumerate(cols_detected.items()):
            col_target = c_grid[i % 4]
            badge_cls = "badge-success" if is_present else "badge-warning"
            col_target.markdown(f"&bull; <code>{col_name}</code>: <span class='{badge_cls}'>{'Detected' if is_present else 'Missing'}</span>", unsafe_allow_html=True)

    if not audit_col_res["has_target"]:
        st.warning("⚠️ Target column **'Amoxicillin'** was not detected in the current dataset. Please load the MCA Research Dataset or upload an AMR dataset containing the 'Amoxicillin' susceptibility column.")
    else:
        # 2. Main Susceptibility Breakdown (Preserves all 3 classes!)
        st.markdown("### 💊 Amoxicillin Susceptibility Profile (3 Clinical Categories)")
        amox_counts, fig_amox = analyze_amoxicillin_distribution(df)

        col_pie, col_tbl = st.columns([1.2, 0.8], gap="medium")
        with col_pie:
            if fig_amox:
                st.plotly_chart(fig_amox, use_container_width=True)
        with col_tbl:
            st.markdown("#### Clinical Category Breakdown")
            st.dataframe(amox_counts, use_container_width=True)
            st.markdown("""
            <div style="font-size:0.8rem; color:#94a3b8; line-height:1.5;">
                <b>CLSI / EUCAST Clinical Definitions:</b><br>
                &bull; <b style="color:#10b981;">Sensitive:</b> High likelihood of therapeutic success with standard dosing.<br>
                &bull; <b style="color:#f59e0b;">Intermediate:</b> Uncertain therapeutic efficacy; requires increased dosage or localized concentration.<br>
                &bull; <b style="color:#f43f5e;">Resistant:</b> High likelihood of clinical failure; alternative antimicrobial regimen required.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 3. Stratified Demographic & Laboratory Factors
        st.markdown("### 🧬 Stratified Resistance Analysis")
        tab_age, tab_spec, tab_genes, tab_panel, tab_sunburst = st.tabs([
            "👶 Demographic: Age Cohorts",
            "🧫 Biological: Specimen Origins",
            "🔬 Molecular: Resistance Genes",
            "💊 Co-Resistance Panel",
            "🌀 AMR Hierarchical Sunburst (NEW)"
        ])

        with tab_age:
            age_ct, fig_age = analyze_resistance_by_age_group(df)
            if fig_age:
                st.plotly_chart(fig_age, use_container_width=True)
                st.dataframe(age_ct, use_container_width=True)
            else:
                st.info("Feature 'Age' not present for age stratification.")

        with tab_spec:
            spec_ct, fig_spec = analyze_resistance_by_specimen(df)
            if fig_spec:
                st.plotly_chart(fig_spec, use_container_width=True)
                st.dataframe(spec_ct, use_container_width=True)
            else:
                st.info("Feature 'Specimen_Type' not present for specimen stratification.")

        with tab_genes:
            genes_ct, fig_genes = analyze_resistance_genes_distribution(df)
            if fig_genes:
                st.plotly_chart(fig_genes, use_container_width=True)
                st.dataframe(genes_ct, use_container_width=True)
            else:
                st.info("Feature 'Resistance_Genes' not present.")

        with tab_panel:
            st.markdown("#### Broad-Spectrum Multi-Antibiotic Co-Resistance Benchmark")
            rates_df, fig_panel = analyze_cross_resistance_panel(df)
            if fig_panel:
                st.plotly_chart(fig_panel, use_container_width=True)
                st.dataframe(rates_df, use_container_width=True)
            else:
                st.info("Insufficient co-antibiotic columns detected for cross-resistance panel benchmarking.")

        with tab_sunburst:
            st.markdown("#### Hierarchical Antimicrobial Resistance Sunburst")
            fig_amr_sun = analyze_amr_hierarchical_sunburst(df)
            if fig_amr_sun:
                st.plotly_chart(fig_amr_sun, use_container_width=True)
            else:
                st.info("Required hierarchy columns (Specimen_Type, Gender, Amoxicillin) not found.")

    # 4. Mandatory Clinical Research Safeguards
    st.markdown("""
    <div class="clinical-disclaimer">
        <b>MANDATORY RESEARCH PRINCIPLES & GOVERNANCE RULES:</b><br>
        1. <b>Association ≠ Causation:</b> Statistical co-occurrence of demographic traits or specimen origins does not imply biological causality.<br>
        2. <b>Identifier Neutrality:</b> <code>Patient_ID</code> must never be used as a predictive feature in downstream machine learning.<br>
        3. <b>Zero Panel Leakage:</b> Co-antibiotic susceptibility outcomes (Ciprofloxacin, Meropenem, etc.) cannot be presumed available prior to Amoxicillin prescribing decisions.<br>
        4. <b>Temporal Integrity:</b> Clinical <code>Outcome</code> represents a post-treatment endpoint and must never be utilized as a pre-treatment predictor.<br>
        5. <b>Clinical Scope:</b> This research platform is strictly designed for retrospective statistical intelligence and decision support, not direct bedside prescriptive therapy.
    </div>
    """, unsafe_allow_html=True)

