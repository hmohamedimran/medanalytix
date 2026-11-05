"""
modules/data_quality.py
-----------------------
Automated, comprehensive healthcare data quality auditing for MEDANALYTIX.
Calculates Quality Scores, audits missingness, duplicates, outliers, and data types.
"""

import pandas as pd
import numpy as np


def compute_column_quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes a comprehensive column-by-column quality audit table:
    - Data Type
    - Non-Null Count
    - Missing Count & Percentage
    - Unique Values Count
    - Outlier Count (if numeric)
    - Whitespace Issue Flag (if string)
    """
    records = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        missing_count = int(series.isnull().sum())
        missing_pct = round((missing_count / total_rows * 100), 2) if total_rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))

        # Check outliers for numeric columns
        outliers_count = 0
        is_numeric = pd.api.types.is_numeric_dtype(series)
        if is_numeric:
            clean_series = series.dropna()
            if len(clean_series) > 4:
                q25 = clean_series.quantile(0.25)
                q75 = clean_series.quantile(0.75)
                iqr = q75 - q25
                if iqr > 0:
                    lower_bound = q25 - (1.5 * iqr)
                    upper_bound = q75 + (1.5 * iqr)
                    outliers_count = int(((clean_series < lower_bound) | (clean_series > upper_bound)).sum())

        # Check whitespace for object/string columns
        whitespace_issues = 0
        is_string_like = pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series)
        if is_string_like:
            str_series = series.dropna().astype(str)
            whitespace_issues = int((str_series != str_series.str.strip()).sum())

        # Quality status indicator
        if missing_pct == 100.0:
            status = "Empty (100% Null)"
        elif missing_pct > 20.0:
            status = "High Missingness"
        elif outliers_count > 0 and whitespace_issues > 0:
            status = "Outliers & Whitespace"
        elif outliers_count > 0:
            status = "Outliers Detected"
        elif whitespace_issues > 0:
            status = "Whitespace Inconsistent"
        elif missing_count > 0:
            status = "Low Missingness"
        else:
            status = "Optimal Quality"

        records.append({
            "Column Name": col,
            "Data Type": dtype,
            "Null Count": missing_count,
            "Missing (%)": missing_pct,
            "Unique Values": unique_count,
            "Outliers (IQR)": outliers_count if is_numeric else "-",
            "Whitespace Issues": whitespace_issues if is_string_like else "-",
            "Quality Status": status
        })

    return pd.DataFrame(records)


def detect_outliers_iqr(df: pd.DataFrame) -> dict:
    """Calculates detailed IQR statistics and outlier counts for all numeric columns."""
    outlier_info = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 4:
            continue
        q25 = float(series.quantile(0.25))
        q75 = float(series.quantile(0.75))
        iqr = q75 - q25
        lower_bound = q25 - (1.5 * iqr)
        upper_bound = q75 + (1.5 * iqr)
        outliers = series[(series < lower_bound) | (series > upper_bound)]

        outlier_info[col] = {
            "q25": round(q25, 2),
            "median": round(float(series.median()), 2),
            "q75": round(q75, 2),
            "iqr": round(float(iqr), 2),
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "outlier_count": len(outliers),
            "outlier_percentage": round(len(outliers) / len(series) * 100, 2)
        }

    return outlier_info


def audit_identifier_columns(df: pd.DataFrame) -> dict:
    """Audits ID columns (like Patient_ID, Sample_ID, Record_ID) for repeats and duplicates."""
    id_cols = [c for c in df.columns if any(k in c.lower() for k in ["id", "patient", "code", "record", "sample"])]
    audit = {}

    for col in id_cols:
        series = df[col]
        total_non_null = series.notnull().sum()
        unique_vals = series.nunique()
        repeats = total_non_null - unique_vals

        audit[col] = {
            "total_records": len(df),
            "non_null_count": int(total_non_null),
            "unique_ids": int(unique_vals),
            "repeated_ids_count": int(repeats),
            "is_unique_primary_key": repeats == 0 and total_non_null == len(df)
        }

    return audit


def calculate_data_quality_score(df: pd.DataFrame) -> tuple[float, str, dict]:
    """
    Computes a composite Data Quality Index (0 - 100%):
    - Completeness penalty (missing cells)
    - Uniqueness penalty (duplicate rows)
    - Consistency penalty (whitespace flaws, outliers)
    """
    total_cells = df.size
    total_rows = len(df)

    if total_cells == 0 or total_rows == 0:
        return 0.0, "Critical Flaws", {}

    # Completeness (40% weight)
    missing_cells = df.isnull().sum().sum()
    completeness_score = max(0.0, (1.0 - (missing_cells / total_cells))) * 40.0

    # Uniqueness (30% weight)
    duplicate_rows = df.duplicated().sum()
    uniqueness_score = max(0.0, (1.0 - (duplicate_rows / total_rows))) * 30.0

    # Consistency & Validity (30% weight)
    whitespace_count = 0
    for col in df.select_dtypes(include=["object"]).columns:
        s = df[col].dropna().astype(str)
        whitespace_count += (s != s.str.strip()).sum()

    outlier_count = 0
    for col in df.select_dtypes(include=[np.number]).columns:
        s = df[col].dropna()
        if len(s) > 4:
            iqr = s.quantile(0.75) - s.quantile(0.25)
            if iqr > 0:
                outlier_count += ((s < s.quantile(0.25) - 1.5*iqr) | (s > s.quantile(0.75) + 1.5*iqr)).sum()

    flaw_ratio = (whitespace_count + outlier_count) / total_cells
    consistency_score = max(0.0, (1.0 - (flaw_ratio * 3.0))) * 30.0

    total_score = round(completeness_score + uniqueness_score + consistency_score, 1)

    if total_score >= 90.0:
        grade = "Excellent (Publication Ready)"
    elif total_score >= 75.0:
        grade = "Good (Minor Cleaning Recommended)"
    elif total_score >= 55.0:
        grade = "Moderate (Requires Preprocessing)"
    else:
        grade = "Poor (Significant Quality Deficits)"

    breakdown = {
        "completeness": round(completeness_score, 1),
        "uniqueness": round(uniqueness_score, 1),
        "consistency": round(consistency_score, 1),
        "total_missing": int(missing_cells),
        "total_duplicates": int(duplicate_rows),
        "total_outliers": int(outlier_count),
        "total_whitespace_flaws": int(whitespace_count)
    }

    return total_score, grade, breakdown
