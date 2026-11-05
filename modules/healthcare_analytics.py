"""
modules/healthcare_analytics.py
-------------------------------
Specialized antimicrobial resistance (AMR) analytics for MEDANALYTIX.
Directly implements the MCA Healthcare Analytics research requirements:
"Analysis and Prediction of Amoxicillin Resistance in Bacterial Isolates Using Machine Learning"
Standardized on the Reddish Neon clinical theme.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from modules.eda_engine import apply_medanalytix_theme, MED_COLORWAY

# Standard Clinical Microbiology Color Mapping
AMOX_COLOR_MAP = {
    "Sensitive": "#10b981",    # Emerald Green
    "Intermediate": "#ffaa00", # Amber Yellow
    "Resistant": "#ff0055"     # Neon Crimson Red
}


def audit_research_columns_presence(df: pd.DataFrame) -> dict:
    """Verifies which standard research columns exist in the dataset."""
    expected_cols = [
        "Patient_ID", "Age", "Gender", "Specimen_Type",
        "Amoxicillin", "Ciprofloxacin", "Meropenem", "Vancomycin", "Colistin",
        "Test_Method", "Resistance_Genes", "Outcome"
    ]
    detected = {col: (col in df.columns) for col in expected_cols}
    has_target = "Amoxicillin" in df.columns
    return {
        "detected": detected,
        "available_count": sum(detected.values()),
        "total_expected": len(expected_cols),
        "has_target": has_target
    }


def analyze_amoxicillin_distribution(df: pd.DataFrame) -> tuple[pd.DataFrame, go.Figure | None]:
    """
    Computes distribution of Sensitive, Intermediate, and Resistant Amoxicillin isolates.
    Preserves all three clinical categories without dropping or premature merging.
    """
    if "Amoxicillin" not in df.columns:
        return pd.DataFrame(), None

    counts = df["Amoxicillin"].value_counts(dropna=False).reset_index()
    counts.columns = ["Clinical Category", "Isolates Count"]
    counts["Percentage"] = (counts["Isolates Count"] / len(df) * 100).round(2)

    # Order by clinical severity: Sensitive -> Intermediate -> Resistant
    order_map = {"Sensitive": 0, "Intermediate": 1, "Resistant": 2}
    counts["sort_order"] = counts["Clinical Category"].map(lambda x: order_map.get(str(x), 99))
    counts = counts.sort_values(by="sort_order").drop(columns=["sort_order"])

    # Donut Pie Chart with Reddish Neon Accents
    colors = [AMOX_COLOR_MAP.get(cat, "#ff2a5f") for cat in counts["Clinical Category"]]
    fig = go.Figure(data=[go.Pie(
        labels=counts["Clinical Category"],
        values=counts["Isolates Count"],
        hole=0.58,
        marker=dict(colors=colors, line=dict(color="#05060b", width=2.5)),
        textinfo="label+percent",
        textfont=dict(size=13, family="Inter, sans-serif"),
        hoverinfo="label+value+percent"
    )])
    fig = apply_medanalytix_theme(fig, title="Amoxicillin Susceptibility Phenotype Distribution (CLSI/EUCAST)")
    return counts, fig


def analyze_resistance_by_age_group(df: pd.DataFrame) -> tuple[pd.DataFrame, go.Figure | None]:
    """Stratifies Amoxicillin resistance across clinical age cohorts."""
    if "Age" not in df.columns or "Amoxicillin" not in df.columns:
        return pd.DataFrame(), None

    temp_df = df.dropna(subset=["Age", "Amoxicillin"]).copy()
    bins = [0, 18, 35, 60, 120]
    labels = ["Pediatric (<18)", "Young Adult (18-35)", "Adult (36-60)", "Geriatric (>60)"]
    temp_df["Age_Group"] = pd.cut(temp_df["Age"], bins=bins, labels=labels, right=False)

    ct = pd.crosstab(temp_df["Age_Group"], temp_df["Amoxicillin"], normalize="index") * 100
    ct = ct.round(2).reset_index()

    melted = ct.melt(id_vars="Age_Group", var_name="Susceptibility", value_name="Percentage")
    fig = px.bar(
        melted,
        x="Age_Group",
        y="Percentage",
        color="Susceptibility",
        barmode="stack",
        color_discrete_map=AMOX_COLOR_MAP,
        text=melted["Percentage"].apply(lambda v: f"{v:.1f}%" if v > 5 else "")
    )
    fig.update_traces(textposition="inside")
    fig = apply_medanalytix_theme(fig, title="Amoxicillin Resistance Across Clinical Age Groups (%)")
    return ct, fig


def analyze_resistance_by_specimen(df: pd.DataFrame) -> tuple[pd.DataFrame, go.Figure | None]:
    """Stratifies Amoxicillin resistance across biological specimen origins."""
    if "Specimen_Type" not in df.columns or "Amoxicillin" not in df.columns:
        return pd.DataFrame(), None

    ct = pd.crosstab(df["Specimen_Type"], df["Amoxicillin"], normalize="index") * 100
    ct = ct.round(2).reset_index()

    melted = ct.melt(id_vars="Specimen_Type", var_name="Susceptibility", value_name="Percentage")
    fig = px.bar(
        melted,
        x="Specimen_Type",
        y="Percentage",
        color="Susceptibility",
        barmode="group",
        color_discrete_map=AMOX_COLOR_MAP,
        text=melted["Percentage"].apply(lambda v: f"{v:.1f}%")
    )
    fig.update_traces(textposition="outside")
    fig = apply_medanalytix_theme(fig, title="Amoxicillin Resistance Profile Stratified by Specimen Type (%)")
    return ct, fig


def analyze_resistance_genes_distribution(df: pd.DataFrame) -> tuple[pd.DataFrame, go.Figure | None]:
    """Analyzes frequency of detected carbapenemase/beta-lactamase resistance genes."""
    if "Resistance_Genes" not in df.columns:
        return pd.DataFrame(), None

    genes_count = df["Resistance_Genes"].value_counts(dropna=False).reset_index()
    genes_count.columns = ["Resistance Gene Profile", "Count"]
    genes_count["Percentage"] = (genes_count["Count"] / len(df) * 100).round(2)

    fig = px.bar(
        genes_count,
        x="Count",
        y="Resistance Gene Profile",
        orientation="h",
        color="Count",
        text=genes_count.apply(lambda r: f"{r['Count']} ({r['Percentage']}%)", axis=1),
        color_continuous_scale=["#140a12", "#ff0055", "#ff6b00"]
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig = apply_medanalytix_theme(fig, title="Molecular Resistance Gene Prevalence (NDM-1, OXA-48, VIM, etc.)")
    return genes_count, fig


def analyze_cross_resistance_panel(df: pd.DataFrame) -> tuple[pd.DataFrame, go.Figure | None]:
    """
    Computes cross-resistance co-occurrence between Amoxicillin and other antibiotic panels:
    Ciprofloxacin, Meropenem, Vancomycin, Colistin.
    """
    abx_list = ["Amoxicillin", "Ciprofloxacin", "Meropenem", "Vancomycin", "Colistin"]
    present_abx = [a for a in abx_list if a in df.columns]

    if len(present_abx) < 2:
        return pd.DataFrame(), None

    rates = []
    for abx in present_abx:
        res_count = (df[abx].astype(str).str.lower() == "resistant").sum()
        total = df[abx].notnull().sum()
        pct = (res_count / total * 100) if total > 0 else 0.0
        rates.append({
            "Antibiotic": abx,
            "Resistant Count": int(res_count),
            "Total Evaluated": int(total),
            "Resistance Rate (%)": round(pct, 2)
        })

    rates_df = pd.DataFrame(rates).sort_values(by="Resistance Rate (%)", ascending=False)

    fig = px.bar(
        rates_df,
        x="Antibiotic",
        y="Resistance Rate (%)",
        text=rates_df["Resistance Rate (%)"].apply(lambda v: f"{v:.1f}%"),
        color="Resistance Rate (%)",
        color_continuous_scale=["#10b981", "#ff6b00", "#ff0055"]
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(yaxis_range=[0, 100])
    fig = apply_medanalytix_theme(fig, title="Comparative Resistance Rates Across Broad-Spectrum Antibiotic Panel")
    return rates_df, fig


def analyze_amr_hierarchical_sunburst(df: pd.DataFrame) -> go.Figure | None:
    """
    NEW CLINICAL CHART: Hierarchical Multi-Level Sunburst Chart
    Drills through Specimen_Type -> Gender -> Amoxicillin Resistance.
    """
    hierarchy_cols = ["Specimen_Type", "Gender", "Amoxicillin"]
    present = [c for c in hierarchy_cols if c in df.columns]
    if len(present) < 2:
        return None

    clean_df = df.dropna(subset=present).copy()
    fig = px.sunburst(
        clean_df,
        path=present,
        color="Amoxicillin" if "Amoxicillin" in present else present[-1],
        color_discrete_map=AMOX_COLOR_MAP
    )
    fig.update_traces(textinfo="label+percent parent", insidetextorientation="radial")
    return apply_medanalytix_theme(fig, title="Hierarchical Path: Specimen Source → Patient Gender → Amoxicillin AMR")
