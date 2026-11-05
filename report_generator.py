"""
modules/report_generator.py
---------------------------
Multi-format research reporting engine for MEDANALYTIX.
Exports multi-sheet Excel workbooks, executive HTML reports, and Markdown summaries.
"""

import io
from datetime import datetime
import pandas as pd
import numpy as np


def generate_multi_sheet_excel(
    df: pd.DataFrame,
    metadata: dict,
    quality_summary_df: pd.DataFrame,
    cleaning_log: list[dict],
    descriptives_df: pd.DataFrame,
    amox_df: pd.DataFrame = None
) -> bytes:
    """Generates an executive multi-sheet Excel research report."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Sheet 1: Executive Overview
        overview_data = [
            {"Metric": "Platform", "Value": "MEDANALYTIX Healthcare Data Intelligence Platform"},
            {"Metric": "Generated At", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"Metric": "Source Dataset", "Value": metadata.get("filename", "N/A")},
            {"Metric": "Total Records", "Value": metadata.get("rows", 0)},
            {"Metric": "Total Features", "Value": metadata.get("columns", 0)},
            {"Metric": "Missing Cell Percentage", "Value": f"{metadata.get('missing_percentage', 0.0)}%"},
            {"Metric": "Duplicate Rows", "Value": metadata.get("duplicate_rows", 0)},
            {"Metric": "Numerical Columns", "Value": len(metadata.get("numerical_columns", []))},
            {"Metric": "Categorical Columns", "Value": len(metadata.get("categorical_columns", []))},
            {"Metric": "MCA Research Target Detected", "Value": "Yes (Amoxicillin AMR)" if metadata.get("is_amoxicillin_research") else "No"}
        ]
        pd.DataFrame(overview_data).to_excel(writer, index=False, sheet_name="Overview")

        # Sheet 2: Cleaned Dataset
        df.to_excel(writer, index=False, sheet_name="Cleaned_Dataset")

        # Sheet 3: Quality Audit
        if not quality_summary_df.empty:
            quality_summary_df.to_excel(writer, index=False, sheet_name="Quality_Audit")

        # Sheet 4: Cleaning Log
        if cleaning_log:
            pd.DataFrame(cleaning_log).to_excel(writer, index=False, sheet_name="Cleaning_Log")
        else:
            pd.DataFrame([{"Notice": "No dataset cleaning transformations performed during this session."}]).to_excel(writer, index=False, sheet_name="Cleaning_Log")

        # Sheet 5: Descriptive Statistics
        if not descriptives_df.empty:
            descriptives_df.to_excel(writer, index=False, sheet_name="Descriptive_Stats")

        # Sheet 6: Healthcare AMR Analysis
        if amox_df is not None and not amox_df.empty:
            amox_df.to_excel(writer, index=False, sheet_name="AMR_Amoxicillin_Profile")

    output.seek(0)
    return output.getvalue()


def generate_executive_html_report(
    df: pd.DataFrame,
    metadata: dict,
    quality_summary_df: pd.DataFrame,
    cleaning_log: list[dict],
    descriptives_df: pd.DataFrame,
    quality_score: float,
    quality_grade: str,
    amox_df: pd.DataFrame = None
) -> str:
    """Generates an executive, print-ready HTML analytical report."""
    timestamp = datetime.now().strftime("%B %d, %Y - %H:%M:%S")

    # Table rows for Quality Audit
    audit_rows = ""
    for _, r in quality_summary_df.iterrows():
        audit_rows += f"""
        <tr>
            <td style="font-weight:600;">{r['Column Name']}</td>
            <td><code>{r['Data Type']}</code></td>
            <td>{r['Null Count']} ({r['Missing (%)']}%)</td>
            <td>{r['Unique Values']}</td>
            <td>{r['Outliers (IQR)']}</td>
            <td><span class="badge">{r['Quality Status']}</span></td>
        </tr>
        """

    # Table rows for Cleaning Log
    cleaning_rows = ""
    if cleaning_log:
        for entry in cleaning_log:
            cleaning_rows += f"""
            <tr>
                <td>{entry['timestamp']}</td>
                <td style="font-weight:600; color:#00f2fe;">{entry['action']}</td>
                <td>{entry['details']}</td>
                <td>{entry['rows_before']} &rarr; {entry['rows_after']}</td>
            </tr>
            """
    else:
        cleaning_rows = "<tr><td colspan='4' style='text-align:center;'>No cleaning modifications were executed. Original data intact.</td></tr>"

    # Healthcare section
    healthcare_html = ""
    if amox_df is not None and not amox_df.empty:
        amox_rows = "".join([f"<tr><td><b>{r['Clinical Category']}</b></td><td>{r['Isolates Count']}</td><td><b>{r['Percentage']}%</b></td></tr>" for _, r in amox_df.iterrows()])
        healthcare_html = f"""
        <div class="card">
            <h2>Clinical Antimicrobial Resistance Profile: Amoxicillin</h2>
            <p>Laboratory Susceptibility Phenotype Breakdown conforming to CLSI / EUCAST clinical breakpoints:</p>
            <table>
                <thead>
                    <tr><th>Phenotypic Category</th><th>Isolate Count</th><th>Proportion (%)</th></tr>
                </thead>
                <tbody>
                    {amox_rows}
                </tbody>
            </table>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>MEDANALYTIX - Executive Healthcare Analytics Report</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            body {{
                font-family: 'Inter', -apple-system, sans-serif;
                background-color: #05060b;
                color: #ffffff;
                margin: 0;
                padding: 40px;
                line-height: 1.6;
            }}
            .header {{
                border-bottom: 2px solid #ff0055;
                padding-bottom: 24px;
                margin-bottom: 32px;
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
            }}
            h1 {{
                margin: 0;
                font-size: 2.2rem;
                background: linear-gradient(135deg, #ff0055 0%, #ff6b00 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .subtitle {{ color: #cbd5e1; font-size: 1rem; margin-top: 6px; }}
            .kpi-container {{
                display: flex;
                gap: 16px;
                margin-bottom: 32px;
                flex-wrap: wrap;
            }}
            .kpi-box {{
                flex: 1;
                min-width: 140px;
                background: #0c0812;
                border: 1px solid rgba(255,0,85,0.2);
                border-radius: 12px;
                padding: 16px 20px;
            }}
            .kpi-label {{ font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; }}
            .kpi-val {{ font-size: 1.8rem; font-weight: 800; color: #ffffff; margin-top: 4px; }}
            .card {{
                background: #0c0812;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 24px;
                margin-bottom: 24px;
            }}
            h2 {{ color: #ff0055; font-size: 1.25rem; margin-top: 0; margin-bottom: 16px; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 12px;
            }}
            th, td {{
                padding: 10px 14px;
                text-align: left;
                border-bottom: 1px solid rgba(255,255,255,0.06);
                font-size: 0.9rem;
            }}
            th {{ background: rgba(255, 0, 85, 0.12); color: #ff0055; font-weight: 600; }}
            code {{ font-family: monospace; color: #ff6b00; background: rgba(255,107,0,0.12); padding: 2px 6px; border-radius: 4px; }}
            .badge {{ background: rgba(255,0,85,0.15); color: #ff0055; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; }}
            .disclaimer {{
                background: rgba(255, 0, 85, 0.09);
                border-left: 4px solid #ff0055;
                padding: 16px 20px;
                border-radius: 0 10px 10px 0;
                color: #ffd1dc;
                font-size: 0.88rem;
                margin-top: 36px;
            }}
            @media print {{
                body {{ background: #ffffff; color: #0f172a; padding: 20px; }}
                .kpi-box, .card {{ background: #ffffff; border: 1px solid #cbd5e1; box-shadow: none; }}
                h1, h2 {{ color: #0f172a; -webkit-text-fill-color: #0f172a; }}
                th {{ background: #f1f5f9; color: #0f172a; }}
                td {{ border-bottom: 1px solid #e2e8f0; color: #0f172a; }}
                .disclaimer {{ background: #fff1f2; color: #9f1239; border-left-color: #e11d48; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>MEDANALYTIX</h1>
                <div class="subtitle">Healthcare Data Intelligence Platform &bull; Analytical Audit Report</div>
            </div>
            <div style="text-align:right; font-size:0.85rem; color:#94a3b8;">
                <div><b>Date:</b> {timestamp}</div>
                <div><b>Dataset:</b> {metadata.get('filename', 'Unknown')}</div>
            </div>
        </div>

        <div class="kpi-container">
            <div class="kpi-box">
                <div class="kpi-label">Total Records</div>
                <div class="kpi-val">{metadata.get('rows', 0):,}</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Features</div>
                <div class="kpi-val">{metadata.get('columns', 0)}</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Data Quality Score</div>
                <div class="kpi-val" style="color:#00f2fe;">{quality_score}/100</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Missing Cells</div>
                <div class="kpi-val">{metadata.get('missing_percentage', 0)}%</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Duplicates</div>
                <div class="kpi-val">{metadata.get('duplicate_rows', 0)}</div>
            </div>
        </div>

        <div class="card">
            <h2>Data Quality Audit Summary (Grade: {quality_grade})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Feature Column</th>
                        <th>Data Type</th>
                        <th>Null Count</th>
                        <th>Unique Values</th>
                        <th>Outliers (IQR)</th>
                        <th>Quality Status</th>
                    </tr>
                </thead>
                <tbody>
                    {audit_rows}
                </tbody>
            </table>
        </div>

        {healthcare_html}

        <div class="card">
            <h2>Data Cleaning & Transformation Audit Trail</h2>
            <table>
                <thead>
                    <tr><th>Timestamp</th><th>Transformation Action</th><th>Operational Details</th><th>Sample Count Delta</th></tr>
                </thead>
                <tbody>
                    {cleaning_rows}
                </tbody>
            </table>
        </div>

        <div class="disclaimer">
            <b>MANDATORY HEALTHCARE RESEARCH DISCLAIMER:</b><br>
            This analytical report is generated for academic, exploratory, and research purposes under MCA Healthcare Analytics methodology.
            All findings, statistical tests, and phenotypic distributions are calculated strictly from the provided retrospective dataset.
            This platform does not prescribe medication, make clinical treatment determinations, or substitute for licensed medical judgment.
            External multi-center clinical validation and standard CLSI / EUCAST laboratory confirmatory assays are mandatory prior to any diagnostic or clinical decision support application.
        </div>
    </body>
    </html>
    """
    return html_content

