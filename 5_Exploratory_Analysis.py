"""
pages/5_Exploratory_Analysis.py
-------------------------------
Interactive Exploratory Data Analysis (EDA) Module for MEDANALYTIX.
Full suite of Plotly Reddish Neon dark-themed interactive visualizations:
Histograms, Boxplots, Violins, Sunbursts, 2D Density Contours, and Radar Telemetry.
"""

import streamlit as st
import pandas as pd
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header,
    check_dataset_or_warn
)
from modules.eda_engine import (
    plot_numerical_distribution,
    plot_categorical_distribution,
    plot_correlation_heatmap,
    plot_box_grouping,
    plot_scatter_2d,
    plot_crosstab_stacked_bar,
    plot_missing_values_matrix,
    plot_violin_distribution,
    plot_hierarchical_sunburst,
    plot_2d_density_contour,
    plot_multivariate_radar
)

st.set_page_config(
    page_title="Exploratory Analysis | MEDANALYTIX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar()

render_page_header(
    title="Exploratory Data Analysis (EDA)",
    subtitle="Interactive univariate, bivariate, hierarchical, and multivariate visual telemetry powered by Plotly.",
    tag="Visual Telemetry Engine"
)

df, metadata = check_dataset_or_warn()

if df is not None and metadata is not None:
    num_cols = metadata["numerical_columns"]
    cat_cols = metadata["categorical_columns"]

    # Extended Tabs with New Advanced Clinical Charts
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Univariate Distribution",
        "🎻 Violin & Dispersion (NEW)",
        "🔥 Correlation Heatmap",
        "🌀 Hierarchical Sunburst (NEW)",
        "📈 Bivariate Scatter & 2D Contour (NEW)",
        "🔄 Cross-Tabulation",
        "📉 Missingness Matrix"
    ])

    # --- TAB 1: Univariate ---
    with tab1:
        st.markdown("### 📊 Single Feature Distribution")
        col_type = st.radio("Select Variable Type", ["Numerical", "Categorical"], horizontal=True)

        if col_type == "Numerical":
            if num_cols:
                sel_num = st.selectbox("Select Numerical Feature", num_cols, key="eda_uni_num")
                n_bins = st.slider("Histogram Bins", min_value=10, max_value=80, value=30, step=5)
                fig_num = plot_numerical_distribution(df, sel_num, n_bins=n_bins)
                st.plotly_chart(fig_num, use_container_width=True)
            else:
                st.warning("No numerical features found in dataset.")
        else:
            if cat_cols:
                sel_cat = st.selectbox("Select Categorical Feature", cat_cols, key="eda_uni_cat")
                fig_cat = plot_categorical_distribution(df, sel_cat)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.warning("No categorical features found in dataset.")

    # --- TAB 2: NEW Violin & Dispersion ---
    with tab2:
        st.markdown("### 🎻 Violin Density & Group Dispersion")
        st.markdown("""
        <p style="color:#cbd5e1; font-size:0.88rem;">
            Combines kernel density estimation (KDE) with boxplots and raw observation jitter to reveal bimodal distribution peaks and clinical skewness.
        </p>
        """, unsafe_allow_html=True)
        if num_cols and cat_cols:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                v_num = st.selectbox("Numerical Metric (Y-Axis)", num_cols, key="violin_num")
            with col_v2:
                v_cat = st.selectbox("Grouping Factor (X-Axis)", cat_cols, key="violin_cat")
            fig_violin = plot_violin_distribution(df, v_num, v_cat)
            st.plotly_chart(fig_violin, use_container_width=True)
        else:
            st.info("Requires at least one numerical and one categorical variable.")

    # --- TAB 3: Correlation Heatmap ---
    with tab3:
        st.markdown("### 🔥 Pearson Correlation Heatmap")
        fig_corr = plot_correlation_heatmap(df)
        if fig_corr:
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("At least two numerical variables are required to generate a correlation heatmap.")

    # --- TAB 4: NEW Hierarchical Sunburst ---
    with tab4:
        st.markdown("### 🌀 Multi-Level Hierarchical Sunburst")
        st.markdown("""
        <p style="color:#cbd5e1; font-size:0.88rem;">
            Drill through multi-layered clinical relationships (e.g., biological source &rarr; diagnostic test &rarr; susceptibility outcome).
        </p>
        """, unsafe_allow_html=True)
        if len(cat_cols) >= 2:
            default_sunburst = [c for c in ["Specimen_Type", "Gender", "Amoxicillin"] if c in cat_cols]
            if len(default_sunburst) < 2:
                default_sunburst = cat_cols[:2]
            sel_sun_cols = st.multiselect("Select Categorical Hierarchy (Order Matters)", cat_cols, default=default_sunburst, key="sunburst_cols")
            if len(sel_sun_cols) >= 2:
                fig_sun = plot_hierarchical_sunburst(df, sel_sun_cols)
                if fig_sun:
                    st.plotly_chart(fig_sun, use_container_width=True)
            else:
                st.warning("Please select at least 2 categorical features to build the hierarchical sunburst.")
        else:
            st.info("At least two categorical features required.")

    # --- TAB 5: Bivariate Scatter & 2D Contour ---
    with tab5:
        st.markdown("### 📈 Bivariate Scatter & Density Contours")
        if len(num_cols) >= 2:
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                scatter_x = st.selectbox("X-Axis Feature", num_cols, index=0, key="scat_x")
            with col_s2:
                scatter_y = st.selectbox("Y-Axis Feature", num_cols, index=min(1, len(num_cols)-1), key="scat_y")
            with col_s3:
                scatter_color = st.selectbox("Color Group (Hue)", ["None"] + cat_cols, key="scat_color")

            sub_plot_type = st.radio("Visualization Mode", ["Scatter Plot with Points", "2D Density Contour Heatmap"], horizontal=True)

            if sub_plot_type == "Scatter Plot with Points":
                fig_scat = plot_scatter_2d(
                    df,
                    x_col=scatter_x,
                    y_col=scatter_y,
                    color_col=None if scatter_color == "None" else scatter_color
                )
                st.plotly_chart(fig_scat, use_container_width=True)
            else:
                fig_contour = plot_2d_density_contour(df, scatter_x, scatter_y)
                st.plotly_chart(fig_contour, use_container_width=True)
        else:
            st.info("At least two numerical features required for bivariate analysis.")

    # --- TAB 6: Cross-Tabulation ---
    with tab6:
        st.markdown("### 🔄 Categorical Cross-Tabulation & Associations")
        if len(cat_cols) >= 2:
            col_ct1, col_ct2, col_ct3 = st.columns([1, 1, 0.8])
            with col_ct1:
                ct_col1 = st.selectbox("Primary Factor (X-Axis)", cat_cols, index=0, key="ct_1")
            with col_ct2:
                ct_col2 = st.selectbox("Secondary Factor (Subgroups)", cat_cols, index=min(1, len(cat_cols)-1), key="ct_2")
            with col_ct3:
                norm_mode = st.radio("Display Mode", ["100% Proportions (%)", "Raw Counts"], key="ct_norm")

            fig_ct = plot_crosstab_stacked_bar(
                df,
                col1=ct_col1,
                col2=ct_col2,
                normalize=(norm_mode == "100% Proportions (%)")
            )
            st.plotly_chart(fig_ct, use_container_width=True)

            st.markdown("#### Contingency Matrix")
            raw_ct = pd.crosstab(df[ct_col1], df[ct_col2], margins=True)
            st.dataframe(raw_ct, use_container_width=True)
        else:
            st.info("At least two categorical features required for cross-tabulation.")

    # --- TAB 7: Missingness Matrix ---
    with tab7:
        st.markdown("### 📉 Missing Data Density Audit")
        fig_miss = plot_missing_values_matrix(df)
        st.plotly_chart(fig_miss, use_container_width=True)
