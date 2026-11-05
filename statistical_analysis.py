"""
modules/statistical_analysis.py
-------------------------------
Statistical inference engine for MEDANALYTIX.
Computes parametric/non-parametric descriptives, Chi-Square tests, Cramér's V,
and ANOVA with automated clinical plain-English interpretations.
"""

import pandas as pd
import numpy as np
from scipy import stats


def compute_numerical_descriptives(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates comprehensive parametric and non-parametric summary statistics."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return pd.DataFrame()

    records = []
    for col in numeric_df.columns:
        s = numeric_df[col].dropna()
        if len(s) == 0:
            continue
        
        q25 = float(s.quantile(0.25))
        q75 = float(s.quantile(0.75))
        iqr = q75 - q25

        records.append({
            "Variable": col,
            "Count": len(s),
            "Mean": round(float(s.mean()), 2),
            "Std Dev": round(float(s.std()), 2),
            "Min": round(float(s.min()), 2),
            "25% (Q1)": round(q25, 2),
            "Median": round(float(s.median()), 2),
            "75% (Q3)": round(q75, 2),
            "Max": round(float(s.max()), 2),
            "IQR": round(float(iqr), 2),
            "Skewness": round(float(s.skew()), 3) if len(s) > 2 else 0.0,
            "Kurtosis": round(float(s.kurt()), 3) if len(s) > 3 else 0.0
        })

    return pd.DataFrame(records)


def compute_categorical_frequencies(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Computes exact counts, proportions, and cumulative percentages for a categorical variable."""
    if col not in df.columns:
        return pd.DataFrame()

    val_counts = df[col].value_counts(dropna=False).reset_index()
    val_counts.columns = ["Category", "Count"]
    total = len(df)
    val_counts["Percentage (%)"] = (val_counts["Count"] / total * 100).round(2)
    val_counts["Cumulative (%)"] = val_counts["Percentage (%)"].cumsum().round(2)
    return val_counts


def run_chi_square_test(df: pd.DataFrame, col1: str, col2: str) -> dict:
    """
    Executes Pearson's Chi-Square Test of Independence for two categorical variables.
    Calculates Degrees of Freedom, Chi2 statistic, p-value, Cramér's V, and contingency table.
    """
    clean_df = df.dropna(subset=[col1, col2])
    contingency = pd.crosstab(clean_df[col1], clean_df[col2])

    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return {
            "error": "At least 2 categories required in both variables to compute Chi-Square."
        }

    chi2, p_val, dof, expected = stats.chi2_contingency(contingency)

    # Cramér's V calculation: sqrt(chi2 / (n * min(r-1, c-1)))
    n = contingency.values.sum()
    min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if (n > 0 and min_dim > 0) else 0.0
    cramers_v = float(round(cramers_v, 4))

    # Plain-English Interpretation
    if p_val < 0.001:
        significance = "Statistically Highly Significant (p < 0.001)"
        p_desc = "Extremely strong statistical evidence to reject the null hypothesis of independence."
    elif p_val < 0.05:
        significance = "Statistically Significant (p < 0.05)"
        p_desc = "Statistically significant evidence of an association between these variables."
    else:
        significance = "Not Statistically Significant (p ≥ 0.05)"
        p_desc = "Insufficient statistical evidence to establish a dependency. Any observed difference could be due to random chance."

    # Effect Size Interpretation
    if cramers_v < 0.1:
        effect_strength = "Negligible Association"
    elif cramers_v < 0.3:
        effect_strength = "Weak Association"
    elif cramers_v < 0.5:
        effect_strength = "Moderate Association"
    else:
        effect_strength = "Strong Association"

    return {
        "col1": col1,
        "col2": col2,
        "chi2_statistic": round(float(chi2), 3),
        "p_value": float(p_val),
        "dof": int(dof),
        "cramers_v": cramers_v,
        "significance": significance,
        "effect_strength": effect_strength,
        "interpretation": f"{significance}. Cramér's V = {cramers_v} indicates a {effect_strength.lower()}. {p_desc}",
        "contingency_table": contingency,
        "expected_frequencies": pd.DataFrame(expected.round(1), index=contingency.index, columns=contingency.columns)
    }


def run_one_way_anova(df: pd.DataFrame, num_col: str, cat_col: str) -> dict:
    """Executes One-Way Analysis of Variance (ANOVA) for numerical mean differences across groups."""
    clean_df = df.dropna(subset=[num_col, cat_col])
    groups = [group[num_col].values for _, group in clean_df.groupby(cat_col) if len(group) > 1]

    if len(groups) < 2:
        return {"error": "Need at least 2 distinct groups with multiple samples to perform ANOVA."}

    f_stat, p_val = stats.f_oneway(*groups)

    if p_val < 0.05:
        interp = f"Statistically significant variance in '{num_col}' across '{cat_col}' cohorts (F={f_stat:.2f}, p={p_val:.4f})."
    else:
        interp = f"No statistically significant difference in '{num_col}' across '{cat_col}' cohorts (F={f_stat:.2f}, p={p_val:.4f})."

    return {
        "num_col": num_col,
        "cat_col": cat_col,
        "f_statistic": round(float(f_stat), 3),
        "p_value": float(p_val),
        "interpretation": interp
    }

