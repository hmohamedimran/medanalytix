"""
pages/2_Upload_Dataset.py
-------------------------
Dataset Upload and Ingestion Module for MEDANALYTIX.
Supports CSV, Excel (XLSX, XLS), and quick-loading of research benchmark files.
"""

import streamlit as st
import pandas as pd
from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header
)
from modules.data_loader import (
    load_uploaded_file,
    load_research_benchmark_dataset,
    initialize_session_dataset,
    get_active_dataset,
    get_formatted_file_size
)

st.set_page_config(
    page_title="Dataset Upload | MEDANALYTIX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar()

render_page_header(
    title="Dataset Upload & Ingestion",
    subtitle="Secure local ingestion for healthcare datasets in CSV, XLSX, and XLS formats.",
    tag="Data Ingestion Module"
)

# Main Container
tab1, tab2 = st.tabs(["📤 Upload New Dataset", "⚡ Load MCA Research Benchmark"])

with tab1:
    st.markdown("""
    <div class="med-card">
        <div class="med-card-header">
            <div class="med-card-title">📁 Drag & Drop Clinical Dataset</div>
            <span class="badge-cyan">Supported: CSV, XLSX, XLS</span>
        </div>
        <p style="color:#94a3b8; font-size:0.88rem; margin-bottom:14px;">
            Datasets are processed entirely in local memory. Zero patient health information is transmitted externally.
        </p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Healthcare Dataset",
        type=["csv", "xlsx", "xls"],
        help="Upload de-identified CSV or Excel files. Maximum recommended file size: 200 MB."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None:
        file_bytes = uploaded_file.size
        df_uploaded, err = load_uploaded_file(uploaded_file)

        if err:
            st.error(f"❌ {err}")
        elif df_uploaded is not None:
            initialize_session_dataset(df_uploaded, filename=uploaded_file.name, file_size_bytes=file_bytes)
            st.success(f"✅ Successfully ingested '{uploaded_file.name}' ({len(df_uploaded):,} rows, {len(df_uploaded.columns)} columns)!")

with tab2:
    st.markdown("""
    <div class="med-card">
        <div class="med-card-header">
            <div class="med-card-title">🔬 Pre-Loaded MCA Research Dataset</div>
            <span class="badge-violet">Antimicrobial Resistance (AMR)</span>
        </div>
        <p style="color:#cbd5e1; font-size:0.92rem;">
            <b>Research Title:</b> <i>"Analysis and Prediction of Amoxicillin Resistance in Bacterial Isolates Using Machine Learning"</i>
        </p>
        <p style="color:#94a3b8; font-size:0.85rem;">
            Loads the verified 2,200 bacterial isolate dataset with clinical antimicrobial susceptibility testing (AST) panels, patient demographics, specimen sources, and molecular beta-lactamase resistance markers.
        </p>
    """, unsafe_allow_html=True)

    if st.button("🚀 Ingest MCA Research Dataset (2,200 Isolates)", use_container_width=True):
        df_bench, err = load_research_benchmark_dataset()
        if df_bench is not None:
            initialize_session_dataset(df_bench, filename="amoxicillin_resistance_tracking.csv", file_size_bytes=233181)
            st.success("✅ Research dataset loaded into active session!")
            st.rerun()
        else:
            st.error(f"❌ Could not load benchmark: {err}")
    st.markdown("</div>", unsafe_allow_html=True)

# Dataset Inspection & Preview
active_df, metadata = get_active_dataset()

if active_df is not None and metadata is not None:
    st.markdown("---")
    st.markdown("### 📊 Ingested Dataset Profile")

    # Ingestion Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", f"{metadata['rows']:,}")
    with col2:
        st.metric("Total Features", f"{metadata['columns']}")
    with col3:
        st.metric("File Size", metadata['file_size'])
    with col4:
        st.metric("Memory Footprint", metadata['memory_usage'])

    # Column Types Breakdown
    col_left, col_right = st.columns([1, 1], gap="medium")
    with col_left:
        st.markdown(f"**Numerical Features ({len(metadata['numerical_columns'])}):**")
        st.code(", ".join(metadata["numerical_columns"]) if metadata["numerical_columns"] else "None", language="text")

    with col_right:
        st.markdown(f"**Categorical / String Features ({len(metadata['categorical_columns'])}):**")
        st.code(", ".join(metadata["categorical_columns"]) if metadata["categorical_columns"] else "None", language="text")

    # Data Preview
    st.markdown("### 🔍 Dataset Preview (First 15 Records)")
    st.dataframe(active_df.head(15), use_container_width=True)

    # Column Schema Detail
    with st.expander("📋 Detailed Column Schema & Null Counts", expanded=False):
        schema_df = pd.DataFrame({
            "Column Name": active_df.columns,
            "Data Type": [str(t) for t in active_df.dtypes],
            "Non-Null Count": active_df.notnull().sum().values,
            "Null Count": active_df.isnull().sum().values,
            "Null (%)": (active_df.isnull().sum().values / len(active_df) * 100).round(2)
        })
        st.dataframe(schema_df, use_container_width=True)

