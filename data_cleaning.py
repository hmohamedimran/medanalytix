"""
modules/data_cleaning.py
------------------------
User-controlled, auditable healthcare dataset cleaning for MEDANALYTIX.
Preserves original raw data while maintaining an immutable transformation log.
"""

import io
from datetime import datetime
import pandas as pd
import numpy as np


def log_cleaning_action(action_name: str, details: str, rows_before: int, rows_after: int) -> dict:
    """Creates a structured record for the cleaning audit log."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action_name,
        "details": details,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_changed": rows_before - rows_after
    }


def remove_duplicate_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Removes exact duplicate rows and logs the operation."""
    rows_before = len(df)
    cleaned_df = df.drop_duplicates().reset_index(drop=True)
    rows_after = len(cleaned_df)
    removed = rows_before - rows_after

    log_entry = log_cleaning_action(
        "Remove Duplicate Rows",
        f"Removed {removed} exact duplicate records.",
        rows_before,
        rows_after
    )
    return cleaned_df, log_entry


def handle_missing_numerical(
    df: pd.DataFrame,
    columns: list[str],
    strategy: str = "Median",
    fill_value: float = 0.0
) -> tuple[pd.DataFrame, list[dict]]:
    """Imputes or drops missing values in specified numerical columns."""
    df_clean = df.copy()
    logs = []

    for col in columns:
        if col not in df_clean.columns:
            continue
        missing_count = int(df_clean[col].isnull().sum())
        if missing_count == 0:
            continue

        rows_before = len(df_clean)

        if strategy == "Mean":
            val = df_clean[col].mean()
            df_clean[col] = df_clean[col].fillna(val)
            details = f"Imputed {missing_count} missing values in '{col}' using mean ({val:.2f})."
        elif strategy == "Median":
            val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(val)
            details = f"Imputed {missing_count} missing values in '{col}' using median ({val:.2f})."
        elif strategy == "Constant":
            df_clean[col] = df_clean[col].fillna(fill_value)
            details = f"Imputed {missing_count} missing values in '{col}' with constant ({fill_value})."
        elif strategy == "Drop Rows":
            df_clean = df_clean.dropna(subset=[col]).reset_index(drop=True)
            details = f"Dropped {missing_count} rows with missing values in '{col}'."
        else:
            continue

        rows_after = len(df_clean)
        logs.append(log_cleaning_action(f"Numerical Imputation ({strategy})", details, rows_before, rows_after))

    return df_clean, logs


def handle_missing_categorical(
    df: pd.DataFrame,
    columns: list[str],
    strategy: str = "Mode",
    custom_label: str = "Unknown / Missing"
) -> tuple[pd.DataFrame, list[dict]]:
    """Imputes or tags missing values in specified categorical columns."""
    df_clean = df.copy()
    logs = []

    for col in columns:
        if col not in df_clean.columns:
            continue
        missing_count = int(df_clean[col].isnull().sum())
        if missing_count == 0:
            continue

        rows_before = len(df_clean)

        if strategy == "Mode":
            mode_series = df_clean[col].mode()
            mode_val = mode_series[0] if not mode_series.empty else custom_label
            df_clean[col] = df_clean[col].fillna(mode_val)
            details = f"Imputed {missing_count} missing values in '{col}' using mode ('{mode_val}')."
        elif strategy == "Explicit Category":
            df_clean[col] = df_clean[col].fillna(custom_label)
            details = f"Preserved {missing_count} missing values in '{col}' as explicit category '{custom_label}'."
        elif strategy == "Drop Rows":
            df_clean = df_clean.dropna(subset=[col]).reset_index(drop=True)
            details = f"Dropped {missing_count} rows with missing values in '{col}'."
        else:
            continue

        rows_after = len(df_clean)
        logs.append(log_cleaning_action(f"Categorical Imputation ({strategy})", details, rows_before, rows_after))

    return df_clean, logs


def standardize_text_columns(
    df: pd.DataFrame,
    columns: list[str],
    strip_whitespace: bool = True,
    case_style: str = "Preserve"
) -> tuple[pd.DataFrame, list[dict]]:
    """Strips leading/trailing whitespace and standardizes casing in text columns."""
    df_clean = df.copy()
    logs = []

    for col in columns:
        if col not in df_clean.columns or df_clean[col].dtype != "object":
            continue

        rows_before = len(df_clean)
        s = df_clean[col].astype(str)

        if strip_whitespace:
            s = s.str.strip()

        if case_style == "Title Case":
            s = s.str.title()
        elif case_style == "Lower Case":
            s = s.str.lower()
        elif case_style == "Upper Case":
            s = s.str.upper()

        df_clean[col] = s
        logs.append(log_cleaning_action(
            "Text Standardization",
            f"Standardized '{col}' (Strip Whitespace: {strip_whitespace}, Case: {case_style}).",
            rows_before,
            rows_before
        ))

    return df_clean, logs


def drop_unnecessary_columns(df: pd.DataFrame, columns_to_drop: list[str]) -> tuple[pd.DataFrame, dict]:
    """Drops specified columns from the dataset."""
    valid_cols = [c for c in columns_to_drop if c in df.columns]
    df_clean = df.drop(columns=valid_cols)
    log_entry = log_cleaning_action(
        "Drop Columns",
        f"Dropped {len(valid_cols)} columns: {', '.join(valid_cols)}.",
        len(df),
        len(df_clean)
    )
    return df_clean, log_entry


def handle_numerical_outliers(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "Clip (Winsorize)"
) -> tuple[pd.DataFrame, list[dict]]:
    """Clips or filters numerical outliers based on Tukey's IQR rule."""
    df_clean = df.copy()
    logs = []

    for col in columns:
        if col not in df_clean.columns or not pd.api.types.is_numeric_dtype(df_clean[col]):
            continue

        series = df_clean[col].dropna()
        if len(series) < 4:
            continue

        q25 = series.quantile(0.25)
        q75 = series.quantile(0.75)
        iqr = q75 - q25
        if iqr <= 0:
            continue

        lower = q25 - 1.5 * iqr
        upper = q75 + 1.5 * iqr

        outlier_mask = (df_clean[col] < lower) | (df_clean[col] > upper)
        outlier_count = int(outlier_mask.sum())
        if outlier_count == 0:
            continue

        rows_before = len(df_clean)

        if method == "Clip (Winsorize)":
            df_clean[col] = df_clean[col].clip(lower=lower, upper=upper)
            details = f"Winsorized {outlier_count} outliers in '{col}' to bounds [{lower:.2f}, {upper:.2f}]."
        elif method == "Remove Outliers":
            df_clean = df_clean[~outlier_mask].reset_index(drop=True)
            details = f"Filtered out {outlier_count} outlier rows in '{col}' outside [{lower:.2f}, {upper:.2f}]."
        else:
            continue

        rows_after = len(df_clean)
        logs.append(log_cleaning_action(f"Outlier Treatment ({method})", details, rows_before, rows_after))

    return df_clean, logs


def export_dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """Converts DataFrame to downloadable CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def export_dataframe_to_excel(df: pd.DataFrame) -> bytes:
    """Converts DataFrame to downloadable Excel XLSX bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cleaned_Data")
    output.seek(0)
    return output.getvalue()
