"""
pages/6_Statistical_Analysis.py
-------------------------------
Statistical Inference & Hypothesis Testing Module for MEDANALYTIX.
Computes parametric/non-parametric summaries, Chi-Square tests, Cramér's V,
and ANOVA with automated clinical plain-English interpretations.
"""

import streamlit as st
import pandas as pd
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header,
    check_dataset_or_warn
)
from modules.statistical_analysis import (
    compute_numerical_descriptives,
    compute_categorical_frequencies,
    run_chi_square_test,
    run_one_way_anova
)

st.set_page_config(
    page_title="Statistical Analysis | MEDANALYTIX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar()

render_page_header(
    title="Statistical Analysis & Inference",
    subtitle="Parametric, non-parametric, and bivariate hypothesis testing with automated plain-English interpretations.",
    tag="Biostatistical Inference Engine"
)

df, metadata = check_dataset_or_warn()

if df is not None and metadata is not None:
    num_cols = metadata["numerical_columns"]
    cat_cols = metadata["categorical_columns"]

    tab_desc, tab_chi, tab_anova = st.tabs([
        "📋 Descriptive Statistics",
        "📐 Chi-Square & Cramér's V (Categorical)",
        "🧪 One-Way ANOVA (Numeric across Groups)"
    ])

    # --- TAB 1: Descriptive Statistics ---
    with tab_desc:
        st.markdown("### 📊 Numerical Descriptives Table")
        if num_cols:
            df_desc = compute_numerical_descriptives(df)
            st.dataframe(df_desc, use_container_width=True)
            st.markdown("""
            <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">
                <b>Statistical Glossary:</b> 
                <b>Mean:</b> Parametric average. 
                <b>Median:</b> 50th percentile (robust to outliers). 
                <b>IQR:</b> Interquartile Range (Q3 - Q1). 
                <b>Skewness:</b> Symmetry of distribution (0 = normal). 
                <b>Kurtosis:</b> Tail heaviness relative to normal distribution.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No numerical variables available.")

        st.markdown("---")
        st.markdown("### 🏷️ Categorical Frequency Distribution")
        if cat_cols:
            sel_freq_cat = st.selectbox("Select Categorical Feature", cat_cols, key="stat_freq_cat")
            df_freq = compute_categorical_frequencies(df, sel_freq_cat)
            st.dataframe(df_freq, use_container_width=True)
        else:
            st.info("No categorical variables available.")

    # --- TAB 2: Chi-Square Test of Independence ---
    with tab_chi:
        st.markdown("### 📐 Pearson's Chi-Square Test of Independence (χ²)")
        st.markdown("""
        <p style="color:#94a3b8; font-size:0.88rem;">
            Evaluates whether an observed association between two categorical clinical variables is statistically significant or attributable to random sampling variability.
        </p>
        """, unsafe_allow_html=True)

        if len(cat_cols) >= 2:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                chi_var1 = st.selectbox("Variable 1 (e.g. Amoxicillin)", cat_cols, index=0, key="chi_v1")
            with col_c2:
                chi_var2 = st.selectbox("Variable 2 (e.g. Specimen_Type)", cat_cols, index=min(1, len(cat_cols)-1), key="chi_v2")

            if chi_var1 != chi_var2:
                res = run_chi_square_test(df, chi_var1, chi_var2)
                if "error" in res:
                    st.error(res["error"])
                else:
                    # Results Metric Banner
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    with col_m1:
                        st.metric("Chi-Square Statistic (χ²)", f"{res['chi2_statistic']}")
                    with col_m2:
                        p_val_display = "< 0.0001" if res['p_value'] < 0.0001 else f"{res['p_value']:.4f}"
                        st.metric("p-Value", p_val_display)
                    with col_m3:
                        st.metric("Degrees of Freedom (df)", f"{res['dof']}")
                    with col_m4:
                        st.metric("Cramér's V (Effect Size)", f"{res['cramers_v']}")

                    # Interpretation Box
                    badge_style = "badge-success" if res['p_value'] < 0.05 else "badge-warning"
                    st.markdown(f"""
                    <div class="med-card" style="border-left: 4px solid {'#10b981' if res['p_value'] < 0.05 else '#f59e0b'};">
                        <div style="font-weight:700; font-size:1.05rem; color:#ffffff; margin-bottom:6px;">
                            Clinical Research Interpretation: <span class="{badge_style}">{res['significance']}</span>
                        </div>
                        <p style="color:#cbd5e1; font-size:0.92rem; margin:0;">
                            {res['interpretation']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Tables
                    st.markdown("#### Observed Contingency Table (Counts)")
                    st.dataframe(res["contingency_table"], use_container_width=True)

                    with st.expander("🔬 View Expected Frequencies (Under Null Hypothesis)", expanded=False):
                        st.dataframe(res["expected_frequencies"], use_container_width=True)
            else:
                st.warning("Please select two distinct categorical variables for Chi-Square testing.")
        else:
            st.info("At least two categorical features required for Chi-Square analysis.")

    # --- TAB 3: One-Way ANOVA ---
    with tab_anova:
        st.markdown("### 🧪 One-Way Analysis of Variance (ANOVA)")
        st.markdown("""
        <p style="color:#94a3b8; font-size:0.88rem;">
            Tests whether the mean of a continuous numerical variable (e.g. Patient Age) differs significantly across independent categorical clinical groups (e.g. Amoxicillin Susceptibility).
        </p>
        """, unsafe_allow_html=True)

        if num_cols and cat_cols:
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                anova_num = st.selectbox("Continuous Metric (e.g. Age)", num_cols, key="anova_n")
            with col_a2:
                anova_cat = st.selectbox("Cohort Grouping (e.g. Amoxicillin)", cat_cols, key="anova_c")

            res_anova = run_one_way_anova(df, anova_num, anova_cat)
            if "error" in res_anova:
                st.error(res_anova["error"])
            else:
                c_a1, c_a2 = st.columns(2)
                with c_a1:
                    st.metric("F-Statistic", f"{res_anova['f_statistic']}")
                with c_a2:
                    p_disp = "< 0.0001" if res_anova['p_value'] < 0.0001 else f"{res_anova['p_value']:.4f}"
                    st.metric("p-Value", p_disp)

                st.markdown(f"""
                <div class="med-card">
                    <div style="font-weight:700; color:#00f2fe; margin-bottom:4px;">ANOVA Determination:</div>
                    <p style="color:#cbd5e1; font-size:0.92rem; margin:0;">
                        {res_anova['interpretation']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Group-wise summary
                st.markdown(f"#### Mean & Standard Deviation of '{anova_num}' by '{anova_cat}'")
                group_stats = df.groupby(anova_cat)[anova_num].agg(["count", "mean", "std", "median"]).reset_index()
                group_stats["mean"] = group_stats["mean"].round(2)
                group_stats["std"] = group_stats["std"].round(2)
                st.dataframe(group_stats, use_container_width=True)
        else:
            st.info("Requires at least one numerical and one categorical variable.")

