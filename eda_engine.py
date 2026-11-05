"""
modules/eda_engine.py
---------------------
Interactive, publication-grade healthcare EDA visualizations using Plotly.
Standardized on the MEDANALYTIX Reddish Neon SaaS theme:
Deep Obsidian Black (#05060b) + Neon Crimson Red (#ff0055) + Neon Coral (#ff6b00).
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Master Reddish Neon Theme Constants
THEME_BG_MAIN = "#05060b"
THEME_BG_PLOT = "#0c0812"
THEME_TEXT_PRIMARY = "#ffffff"
THEME_TEXT_MUTED = "#cbd5e1"
THEME_GRID = "rgba(255, 255, 255, 0.08)"

# Vibrant Reddish Neon Colorway
MED_COLORWAY = [
    "#ff0055",  # Neon Crimson Red
    "#ff6b00",  # Neon Coral Flame
    "#ff2a5f",  # Electric Rose
    "#ff8800",  # Neon Amber
    "#ff007f",  # Neon Magenta
    "#f43f5e",  # Crimson Rose
    "#ff5400",  # Blaze Orange
    "#10b981"   # Emerald Accent
]


def apply_medanalytix_theme(fig: go.Figure, title: str = "", height: int = 490) -> go.Figure:
    """Applies standardized MEDANALYTIX Reddish Neon dark styling to any Plotly figure."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "font": {"size": 16, "color": THEME_TEXT_PRIMARY, "family": "Inter, sans-serif"},
            "x": 0.02,
            "xanchor": "left"
        },
        paper_bgcolor=THEME_BG_MAIN,
        plot_bgcolor=THEME_BG_PLOT,
        font={"family": "Inter, sans-serif", "color": THEME_TEXT_MUTED, "size": 12},
        colorway=MED_COLORWAY,
        height=height,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            bgcolor="rgba(20, 10, 18, 0.85)",
            bordercolor="rgba(255, 0, 85, 0.25)",
            borderwidth=1,
            font={"color": THEME_TEXT_PRIMARY}
        ),
        hoverlabel=dict(
            bgcolor="#140a12",
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor="#ff0055"
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=THEME_GRID,
        zerolinecolor=THEME_GRID,
        tickfont={"color": THEME_TEXT_MUTED}
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=THEME_GRID,
        zerolinecolor=THEME_GRID,
        tickfont={"color": THEME_TEXT_MUTED}
    )
    return fig


def plot_numerical_distribution(df: pd.DataFrame, column: str, n_bins: int = 30) -> go.Figure:
    """Creates an interactive distribution histogram with box plot overlay."""
    fig = px.histogram(
        df,
        x=column,
        nbins=n_bins,
        marginal="box",
        color_discrete_sequence=["#ff0055"],
        opacity=0.85
    )
    fig.update_traces(marker_line_color="#05060b", marker_line_width=1)
    return apply_medanalytix_theme(fig, title=f"Distribution Analysis: {column}")


def plot_categorical_distribution(df: pd.DataFrame, column: str, max_categories: int = 15) -> go.Figure:
    """Creates a horizontal bar chart of category frequencies and percentages."""
    counts = df[column].value_counts(dropna=False).head(max_categories).reset_index()
    counts.columns = [column, "Count"]
    counts["Percentage"] = (counts["Count"] / len(df) * 100).round(2)
    counts = counts.sort_values(by="Count", ascending=True)

    fig = px.bar(
        counts,
        x="Count",
        y=column,
        orientation="h",
        text=counts.apply(lambda r: f"{r['Count']} ({r['Percentage']}%)", axis=1),
        color="Count",
        color_continuous_scale=["#1a0812", "#ff0055", "#ff6b00"]
    )
    fig.update_traces(textposition="outside", marker_line_color="#05060b", marker_line_width=1)
    fig.update_coloraxes(showscale=False)
    return apply_medanalytix_theme(fig, title=f"Frequency Breakdown: {column}")


def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure | None:
    """Generates an interactive correlation heatmap for numerical variables."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return None

    corr = numeric_df.corr().round(2)
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[[0, "#0c0812"], [0.5, "#ff6b00"], [1, "#ff0055"]],
        zmin=-1,
        zmax=1
    )
    return apply_medanalytix_theme(fig, title="Pearson Correlation Matrix (Numerical Features)")


def plot_box_grouping(df: pd.DataFrame, num_col: str, cat_col: str) -> go.Figure:
    """Generates stratified box plots for comparing numeric distributions across groups."""
    fig = px.box(
        df,
        x=cat_col,
        y=num_col,
        color=cat_col,
        points="outliers",
        color_discrete_sequence=MED_COLORWAY
    )
    return apply_medanalytix_theme(fig, title=f"{num_col} Stratified by {cat_col}")


def plot_scatter_2d(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None = None) -> go.Figure:
    """Generates an interactive 2D scatter plot with trendline or category hue."""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col if color_col in df.columns else None,
        color_discrete_sequence=MED_COLORWAY,
        opacity=0.88
    )
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color="#05060b")))
    return apply_medanalytix_theme(fig, title=f"Bivariate Scatter: {x_col} vs {y_col}")


def plot_crosstab_stacked_bar(df: pd.DataFrame, col1: str, col2: str, normalize: bool = True) -> go.Figure:
    """Generates 100% stacked bar chart or absolute count cross-tabulation."""
    ct = pd.crosstab(df[col1], df[col2], normalize="index" if normalize else False)
    if normalize:
        ct = (ct * 100).round(2)

    ct_reset = ct.reset_index().melt(id_vars=col1, value_name="Value", var_name=col2)

    fig = px.bar(
        ct_reset,
        x=col1,
        y="Value",
        color=col2,
        barmode="stack",
        color_discrete_sequence=MED_COLORWAY,
        text=ct_reset["Value"].apply(lambda v: f"{v:.1f}%" if normalize and v > 4 else (f"{int(v)}" if not normalize and v > 0 else ""))
    )
    fig.update_traces(textposition="inside")
    y_label = "Percentage (%)" if normalize else "Isolate Count"
    fig.update_layout(yaxis_title=y_label)
    return apply_medanalytix_theme(fig, title=f"Cross-Tabulation: {col1} by {col2} ({y_label})")


def plot_missing_values_matrix(df: pd.DataFrame) -> go.Figure:
    """Generates a bar chart visualizing missing values count and percentage per column."""
    missing = df.isnull().sum().reset_index()
    missing.columns = ["Column", "Missing Count"]
    missing["Missing (%)"] = (missing["Missing Count"] / len(df) * 100).round(2)
    missing = missing.sort_values(by="Missing Count", ascending=False)

    fig = px.bar(
        missing,
        x="Column",
        y="Missing (%)",
        text=missing.apply(lambda r: f"{r['Missing Count']} ({r['Missing (%)']}%)" if r['Missing Count'] > 0 else "0", axis=1),
        color="Missing (%)",
        color_continuous_scale=["#10b981", "#ff6b00", "#ff0055"]
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(yaxis_range=[0, max(100, missing["Missing (%)"].max() + 15)])
    return apply_medanalytix_theme(fig, title="Missingness Audit per Feature Column (%)")


# ==============================================================================
# NEW ADVANCED CLINICAL CHARTS (REDDISH NEON SUITE)
# ==============================================================================

def plot_violin_distribution(df: pd.DataFrame, num_col: str, cat_col: str) -> go.Figure:
    """
    NEW CHART 1: Interactive Violin Plot with Embedded Boxplot and KDE Density.
    Reveals bimodal clinical peaks and density distributions across groups.
    """
    fig = px.violin(
        df,
        y=num_col,
        x=cat_col,
        color=cat_col,
        box=True,
        points="all",
        hover_data=df.columns,
        color_discrete_sequence=MED_COLORWAY
    )
    fig.update_traces(meanline_visible=True, opacity=0.85)
    return apply_medanalytix_theme(fig, title=f"Violin Density & Outlier Dispersion: {num_col} by {cat_col}")


def plot_hierarchical_sunburst(df: pd.DataFrame, path_cols: list[str]) -> go.Figure | None:
    """
    NEW CHART 2: Interactive Hierarchical Sunburst Chart.
    Allows multi-layered drilling through clinical hierarchies:
    e.g. Specimen_Type -> Gender -> Amoxicillin Susceptibility.
    """
    valid_cols = [c for c in path_cols if c in df.columns]
    if len(valid_cols) < 2:
        return None

    clean_df = df.dropna(subset=valid_cols).copy()
    fig = px.sunburst(
        clean_df,
        path=valid_cols,
        color=valid_cols[-1],
        color_discrete_sequence=MED_COLORWAY
    )
    fig.update_traces(textinfo="label+percent parent", insidetextorientation="radial")
    hierarchy_label = " → ".join(valid_cols)
    return apply_medanalytix_theme(fig, title=f"Hierarchical Sunburst: {hierarchy_label}")


def plot_2d_density_contour(df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
    """
    NEW CHART 3: 2D Bivariate Density Contour / KDE Heatmap.
    Reveals observational clusters, hot spots, and density ridges between continuous clinical markers.
    """
    fig = px.density_contour(
        df,
        x=x_col,
        y=y_col,
        color_discrete_sequence=["#ff0055"]
    )
    fig.update_traces(contours_coloring="fill", contours_showlabels=True, colorscale="Hot")
    return apply_medanalytix_theme(fig, title=f"2D Bivariate Density Contour: {x_col} vs {y_col}")


def plot_multivariate_radar(df: pd.DataFrame, group_col: str, metrics: list[str]) -> go.Figure | None:
    """
    NEW CHART 4: Multivariate Radar / Spider Chart.
    Normalizes continuous clinical metrics across categories to compare clinical phenotypes.
    """
    valid_metrics = [m for m in metrics if m in df.columns and pd.api.types.is_numeric_dtype(df[m])]
    if len(valid_metrics) < 3 or group_col not in df.columns:
        return None

    grouped = df.groupby(group_col)[valid_metrics].mean().reset_index()

    fig = go.Figure()
    for idx, row in grouped.iterrows():
        r_vals = list(row[valid_metrics].values)
        r_vals.append(r_vals[0])  # Close radar loop
        theta_labels = valid_metrics + [valid_metrics[0]]

        fig.add_trace(go.Scatterpolar(
            r=r_vals,
            theta=theta_labels,
            fill="toself",
            name=str(row[group_col]),
            line=dict(color=MED_COLORWAY[idx % len(MED_COLORWAY)], width=2),
            opacity=0.75
        ))

    fig.update_layout(
        polar=dict(
            bgcolor=THEME_BG_PLOT,
            radialaxis=dict(visible=True, showgrid=True, gridcolor=THEME_GRID, tickfont=dict(color=THEME_TEXT_MUTED)),
            angularaxis=dict(gridcolor=THEME_GRID, tickfont=dict(color=THEME_TEXT_PRIMARY, size=11))
        )
    )
    return apply_medanalytix_theme(fig, title=f"Multivariate Radar Profile Stratified by {group_col}")
