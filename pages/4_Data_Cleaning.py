"""
pages/4_Data_Cleaning.py
------------------------
Interactive, User-Controlled Healthcare Data Cleaning Module for MEDANALYTIX.
Maintains before-and-after parity checks and an immutable audit trail.
"""

import streamlit as st
import pandas as pd
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header,
    check_dataset_or_warn
)
from modules.data_cleaning import (
    remove_duplicate_rows,
    handle_missing_numerical,
    handle_missing_categorical,
    standardize_text_columns,
    drop_unnecessary_columns,
    handle_numerical_outliers,
    export_dataframe_to_csv,
    export_dataframe_to_excel
)
from modules.data_loader import extract_metadata

st.set_page_config(
    page_title="Data Cleaning | MEDANALYTIX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar()

render_page_header(
    title="Data Cleaning & Standardization",
    subtitle="Interactive, non-destructive clinical data remediation with transparent transformation tracking.",
    tag="Data Preprocessing Engine"
)

df, metadata = check_dataset_or_warn()

if df is not None and metadata is not None:
    raw_df = st.session_state.get("raw_df", df)

    # 1. Before vs After Comparison Banner
    raw_missing = int(raw_df.isnull().sum().sum())
    curr_missing = int(df.isnull().sum().sum())
    raw_dups = int(raw_df.duplicated().sum())
    curr_dups = int(df.duplicated().sum())

    st.markdown("### 📊 Dataset State Comparison")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Records", f"{len(df):,}", delta=f"{len(df) - len(raw_df)} from raw")
    with c2:
        st.metric("Features Count", f"{len(df.columns)}", delta=f"{len(df.columns) - len(raw_df.columns)} from raw")
    with c3:
        st.metric("Missing Cells", f"{curr_missing:,}", delta=f"{curr_missing - raw_missing} cells", delta_color="inverse")
    with c4:
        st.metric("Duplicate Rows", f"{curr_dups:,}", delta=f"{curr_dups - raw_dups} rows", delta_color="inverse")

    st.markdown("---")

    # 2. Interactive Cleaning Toolkit
    st.markdown("### 🛠️ User-Controlled Remediation Operations")

    col_op1, col_op2 = st.columns(2, gap="medium")

    # --- Operation 1: Remove Duplicate Rows ---
    with col_op1:
        st.markdown("""
        <div class="med-card">
            <div class="med-card-header">
                <div class="med-card-title">1. Deduplication</div>
                <span class="badge-cyan">Exact Match</span>
            </div>
            <p style="font-size:0.85rem; color:#94a3b8;">
                Eliminates exact duplicate rows where every feature value is identical across records.
            </p>
        """, unsafe_allow_html=True)
        if st.button("🧹 Remove Duplicate Rows", use_container_width=True):
            clean_df, log_entry = remove_duplicate_rows(df)
            st.session_state["active_df"] = clean_df
            st.session_state["cleaning_log"].append(log_entry)
            st.session_state["dataset_metadata"] = extract_metadata(clean_df, filename=metadata["filename"])
            st.success(f"Deduplication complete: {log_entry['details']}")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Operation 2: Text Standardization ---
    with col_op2:
        st.markdown("""
        <div class="med-card">
            <div class="med-card-header">
                <div class="med-card-title">2. Text Formatting & Whitespace</div>
                <span class="badge-violet">String Cleaning</span>
            </div>
            <p style="font-size:0.85rem; color:#94a3b8;">
                Strips hidden leading/trailing spaces and harmonizes letter casing.
            </p>
        """, unsafe_allow_html=True)
        text_cols = list(df.select_dtypes(include=["object"]).columns)
        if text_cols:
            sel_text_cols = st.multiselect("Select String Columns to Format", text_cols, default=text_cols[:3], key="text_cols_sel")
            case_opt = st.selectbox("Letter Casing", ["Preserve", "Title Case", "Lower Case", "Upper Case"], key="case_opt_sel")
            if st.button("✨ Standardize Selected Text", use_container_width=True):
                clean_df, logs = standardize_text_columns(df, sel_text_cols, strip_whitespace=True, case_style=case_opt)
                st.session_state["active_df"] = clean_df
                st.session_state["cleaning_log"].extend(logs)
                st.session_state["dataset_metadata"] = extract_metadata(clean_df, filename=metadata["filename"])
                st.success(f"Standardized {len(sel_text_cols)} string features!")
                st.rerun()
        else:
            st.info("No text columns found.")
        st.markdown("</div>", unsafe_allow_html=True)

    col_op3, col_op4 = st.columns(2, gap="medium")

    # --- Operation 3: Missing Numerical Imputation ---
    with col_op3:
        st.markdown("""
        <div class="med-card">
            <div class="med-card-header">
                <div class="med-card-title">3. Missing Numerical Imputation</div>
                <span class="badge-cyan">Quantitative</span>
            </div>
        """, unsafe_allow_html=True)
        num_cols = list(df.select_dtypes(include=[np.number]).columns)
        cols_with_nulls_num = [c for c in num_cols if df[c].isnull().sum() > 0]
        if cols_with_nulls_num:
            sel_num = st.multiselect("Numerical Columns with Nulls", cols_with_nulls_num, default=cols_with_nulls_num, key="num_impute_cols")
            num_strat = st.selectbox("Imputation Technique", ["Median", "Mean", "Constant", "Drop Rows"], key="num_strat_sel")
            const_val = 0.0
            if num_strat == "Constant":
                const_val = st.number_input("Constant Fill Value", value=0.0)
            if st.button("⚡ Apply Numerical Imputation", use_container_width=True):
                clean_df, logs = handle_missing_numerical(df, sel_num, strategy=num_strat, fill_value=const_val)
                st.session_state["active_df"] = clean_df
                st.session_state["cleaning_log"].extend(logs)
                st.session_state["dataset_metadata"] = extract_metadata(clean_df, filename=metadata["filename"])
                st.success(f"Numerical imputation applied using {num_strat}!")
                st.rerun()
        else:
            st.success("✅ Zero missing values in numerical columns!")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Operation 4: Missing Categorical Imputation ---
    with col_op4:
        st.markdown("""
        <div class="med-card">
            <div class="med-card-header">
                <div class="med-card-title">4. Missing Categorical Treatment</div>
                <span class="badge-violet">Qualitative / Clinical</span>
            </div>
        """, unsafe_allow_html=True)
        cat_cols = list(df.select_dtypes(include=["object"]).columns)
        cols_with_nulls_cat = [c for c in cat_cols if df[c].isnull().sum() > 0]
        if cols_with_nulls_cat:
            sel_cat = st.multiselect("Categorical Columns with Nulls", cols_with_nulls_cat, default=cols_with_nulls_cat, key="cat_impute_cols")
            cat_strat = st.selectbox("Categorical Strategy", ["Explicit Category", "Mode", "Drop Rows"], key="cat_strat_sel")
            custom_lbl = "Unknown / Missing"
            if cat_strat == "Explicit Category":
                custom_lbl = st.text_input("Explicit Category Tag", value="Unknown / Not Detected")
            if st.button("🏷️ Apply Categorical Strategy", use_container_width=True):
                clean_df, logs = handle_missing_categorical(df, sel_cat, strategy=cat_strat, custom_label=custom_lbl)
                st.session_state["active_df"] = clean_df
                st.session_state["cleaning_log"].extend(logs)
                st.session_state["dataset_metadata"] = extract_metadata(clean_df, filename=metadata["filename"])
                st.success("Categorical treatment applied successfully!")
                st.rerun()
        else:
            st.success("✅ Zero missing values in categorical columns!")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Operation 5 & 6: Outlier Winsorization & Column Dropping ---
    col_op5, col_op6 = st.columns(2, gap="medium")

    with col_op5:
        st.markdown("""
        <div class="med-card">
            <div class="med-card-header">
                <div class="med-card-title">5. Outlier Treatment (Tukey IQR)</div>
                <span class="badge-cyan">Robust Bounds</span>
            </div>
        """, unsafe_allow_html=True)
        if num_cols:
            sel_outlier_cols = st.multiselect("Select Numeric Columns", num_cols, default=num_cols[:1], key="outlier_cols_sel")
            outlier_strat = st.selectbox("Outlier Remediation Method", ["Clip (Winsorize)", "Remove Outliers"], key="outlier_strat_sel")
            if st.button("📐 Apply Outlier Treatment", use_container_width=True):
                clean_df, logs = handle_numerical_outliers(df, sel_outlier_cols, method=outlier_strat)
                st.session_state["active_df"] = clean_df
                st.session_state["cleaning_log"].extend(logs)
                st.session_state["dataset_metadata"] = extract_metadata(clean_df, filename=metadata["filename"])
                st.success("Outlier bounds adjusted!")
                st.rerun()
        else:
            st.info("No numerical features available.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_op6:
        st.markdown("""
        <div class="med-card">
            <div class="med-card-header">
                <div class="med-card-title">6. Drop Unnecessary Columns</div>
                <span class="badge-danger">Dimensionality</span>
            </div>
        """, unsafe_allow_html=True)
        drop_candidate_cols = st.multiselect("Select Columns to Remove", list(df.columns), key="drop_cols_sel")
        if st.button("🗑️ Drop Selected Columns", use_container_width=True):
            if drop_candidate_cols:
                clean_df, log_entry = drop_unnecessary_columns(df, drop_candidate_cols)
                st.session_state["active_df"] = clean_df
                st.session_state["cleaning_log"].append(log_entry)
                st.session_state["dataset_metadata"] = extract_metadata(clean_df, filename=metadata["filename"])
                st.success(f"Removed {len(drop_candidate_cols)} columns.")
                st.rerun()
            else:
                st.warning("Please select at least one column to remove.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # 3. Live Cleaning Audit Trail
    st.markdown("### 📜 Transformation Audit Trail")
    cleaning_log = st.session_state.get("cleaning_log", [])
    if cleaning_log:
        df_log = pd.DataFrame(cleaning_log)
        st.dataframe(df_log, use_container_width=True)
    else:
        st.info("No cleaning transformations have been applied yet during this session.")

    # 4. Preview Cleaned Dataset
    st.markdown("### 🔍 Cleaned Dataset Preview (First 15 Rows)")
    st.dataframe(df.head(15), use_container_width=True)

    # 5. Export Cleaned Dataset
    st.markdown("### 📥 Export Cleaned Dataset")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_bytes = export_dataframe_to_csv(df)
        st.download_button(
            label="💾 Download Cleaned CSV",
            data=csv_bytes,
            file_name="medanalytix_cleaned_dataset.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl2:
        excel_bytes = export_dataframe_to_excel(df)
        st.download_button(
            label="📊 Download Cleaned Excel (.xlsx)",
            data=excel_bytes,
            file_name="medanalytix_cleaned_dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
