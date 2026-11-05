"""
modules/data_loader.py
----------------------
Robust data ingestion and session management for MEDANALYTIX.
Supports CSV, XLSX, XLS with automatic metadata profiling.
"""

import os
import io
import pandas as pd
import numpy as np
import streamlit as st


def get_formatted_file_size(size_bytes: int) -> str:
    """Returns human-readable file size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def detect_column_types(df: pd.DataFrame) -> dict:
    """Classifies DataFrame columns into numerical, categorical, and datetime."""
    numerical_cols = list(df.select_dtypes(include=[np.number]).columns)
    datetime_cols = list(df.select_dtypes(include=["datetime", "datetimetz"]).columns)
    
    # Categorical includes object, category, string, bool
    categorical_cols = [c for c in df.columns if c not in numerical_cols and c not in datetime_cols]
    
    return {
        "numerical": numerical_cols,
        "categorical": categorical_cols,
        "datetime": datetime_cols,
        "all": list(df.columns)
    }


def is_amoxicillin_research_dataset(df: pd.DataFrame) -> bool:
    """
    Checks if the loaded dataset contains the core columns from the MCA research project:
    'Analysis and Prediction of Amoxicillin Resistance in Bacterial Isolates Using Machine Learning'
    """
    core_cols = {"Age", "Gender", "Specimen_Type", "Amoxicillin"}
    dataset_cols = set(df.columns)
    return core_cols.issubset(dataset_cols)


def extract_metadata(df: pd.DataFrame, filename: str = "dataset.csv", file_size_bytes: int = 0) -> dict:
    """Generates a complete metadata profile of the ingested dataset."""
    col_types = detect_column_types(df)
    total_cells = df.size
    total_missing = int(df.isnull().sum().sum())
    missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0.0
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = (duplicate_rows / len(df) * 100) if len(df) > 0 else 0.0

    memory_bytes = int(df.memory_usage(deep=True).sum())

    is_research = is_amoxicillin_research_dataset(df)

    return {
        "filename": filename,
        "file_size": get_formatted_file_size(file_size_bytes) if file_size_bytes > 0 else "Local / Memory",
        "file_size_bytes": file_size_bytes,
        "rows": len(df),
        "columns": len(df.columns),
        "total_cells": total_cells,
        "total_missing": total_missing,
        "missing_percentage": round(missing_pct, 2),
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": round(duplicate_pct, 2),
        "memory_usage": get_formatted_file_size(memory_bytes),
        "numerical_columns": col_types["numerical"],
        "categorical_columns": col_types["categorical"],
        "datetime_columns": col_types["datetime"],
        "all_columns": col_types["all"],
        "is_amoxicillin_research": is_research
    }


def load_uploaded_file(uploaded_file) -> tuple[pd.DataFrame | None, str | None]:
    """
    Safely parses an uploaded Streamlit file (CSV, XLSX, XLS).
    Returns (DataFrame, error_message).
    """
    if uploaded_file is None:
        return None, "No file uploaded."

    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext == ".csv":
            # Attempt UTF-8 with fallback
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="latin1")
        elif ext in [".xlsx", ".xls"]:
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file)
        else:
            return None, f"Unsupported file extension: '{ext}'. Please upload CSV or Excel files."

        if df.empty:
            return None, "The uploaded file is empty."

        return df, None

    except Exception as e:
        return None, f"Error parsing file: {str(e)}"


def load_research_benchmark_dataset() -> tuple[pd.DataFrame | None, str | None]:
    """
    Loads the MCA research dataset from local disk for seamless demo verification.
    Tries cleaned_dataset.csv or antibiotic_resistance_tracking.csv.
    """
    candidate_paths = [
        os.path.join("I:", os.sep, "imran", "preprocessing_output", "cleaned_dataset.csv"),
        os.path.join("I:", os.sep, "imran", "antibiotic_resistance_tracking.csv"),
        os.path.join("..", "preprocessing_output", "cleaned_dataset.csv"),
        os.path.join("..", "antibiotic_resistance_tracking.csv")
    ]

    for path in candidate_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                return df, None
            except Exception as e:
                return None, f"Failed reading benchmark file at {path}: {str(e)}"

    return None, "MCA research benchmark dataset not found in standard paths."


def initialize_session_dataset(df: pd.DataFrame, filename: str = "dataset.csv", file_size_bytes: int = 0):
    """Initializes or resets dataset states in Streamlit session_state."""
    st.session_state["raw_df"] = df.copy()
    st.session_state["cleaned_df"] = df.copy()
    st.session_state["active_df"] = df.copy()
    st.session_state["dataset_metadata"] = extract_metadata(df, filename=filename, file_size_bytes=file_size_bytes)
    
    if "cleaning_log" not in st.session_state:
        st.session_state["cleaning_log"] = []
    
    # Track recent operations
    if "recent_operations" not in st.session_state:
        st.session_state["recent_operations"] = []
    st.session_state["recent_operations"].append(f"Loaded dataset '{filename}' ({len(df)} rows, {len(df.columns)} columns)")


def get_active_dataset() -> tuple[pd.DataFrame | None, dict | None]:
    """Retrieves current active dataset and metadata from session state."""
    active_df = st.session_state.get("active_df", None)
    metadata = st.session_state.get("dataset_metadata", None)
    return active_df, metadata

