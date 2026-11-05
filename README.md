# 🧬 MEDANALYTIX — Healthcare Data Intelligence Platform

**Master of Computer Applications (MCA) Healthcare Analytics Research Project**  
*Title:* **"Analysis and Prediction of Amoxicillin Resistance in Bacterial Isolates Using Machine Learning"**

---

## 🌟 Executive Overview

**MEDANALYTIX** is a commercial-grade healthcare data analytics web application developed with Python and Streamlit. Built specifically for biostatisticians, clinical microbiologists, and healthcare data analysts, the platform transforms raw, noisy healthcare datasets into publication-ready clinical intelligence through automated quality auditing, non-destructive data cleaning, interactive exploratory data analysis, and inferential hypothesis testing.

### ✨ Key Capabilities

- **Executive Telemetry:** Dynamic KPI metric tiles, composite Data Quality Index (0–100%), and active RAM monitoring.
- **Multimodal Data Ingestion:** Seamless drag-and-drop ingestion of CSV, XLSX, and XLS datasets with automatic schema detection.
- **Automated Data Quality Audit:** Completeness scoring, identifier duplication auditing, outlier detection via Tukey’s IQR rule, and whitespace diagnostics.
- **User-Controlled Data Remediation:** Transparent, non-destructive cleaning with before-and-after metric parity checks and an immutable audit trail.
- **Interactive Visual Telemetry:** Publication-grade Plotly visualizations standardizing on an Obsidian Black (`#050811`), Neon Cyan (`#00f2fe`), and Electric Violet (`#8b5cf6`) design language.
- **Clinical AMR Intelligence:** Dedicated antimicrobial resistance module recognizing CLSI/EUCAST phenotypic categories (Sensitive, Intermediate, Resistant), age-cohort stratification, specimen origins, and molecular resistance gene prevalence (NDM-1, OXA-48, VIM).
- **Biostatistical Inference Engine:** Parametric and non-parametric summary statistics, Pearson’s Chi-Square Test of Independence ($\chi^2$), Cramér’s V effect size calculation, and One-Way ANOVA with plain-English interpretations.
- **Multi-Format Research Export:** Multi-sheet formatted Excel workbooks (`.xlsx`), executive print-ready HTML/PDF reports, cleaned CSVs, and Markdown summaries.

---

## 🏗️ Project Architecture

```text
medanalytix/
├── app.py                      # Main entrypoint & executive dashboard
├── requirements.txt            # System dependencies
├── README.md                   # Project documentation & run guide
│
├── pages/                      # Multi-page application modules
│   ├── 1_Overview.py           # Overview Dashboard & telemetry
│   ├── 2_Upload_Dataset.py     # Dataset Ingestion (CSV / XLSX / XLS)
│   ├── 3_Data_Quality.py       # Automated Data Quality Audit
│   ├── 4_Data_Cleaning.py      # User-Controlled Remediation Engine
│   ├── 5_Exploratory_Analysis.py # Plotly Interactive EDA Visualizations
│   ├── 6_Statistical_Analysis.py # Chi-Square, Cramér's V, ANOVA, Descriptives
│   ├── 7_Healthcare_Insights.py # Antimicrobial Resistance (AMR) Intelligence
│   ├── 8_Reports.py            # Multi-Sheet Excel, HTML/PDF, CSV Reports
│   └── 9_About.py              # Architecture, Privacy & Governance
│
├── modules/                    # Modular Python backend engines
│   ├── __init__.py
│   ├── data_loader.py          # File ingestion, metadata profiling, session state
│   ├── data_quality.py         # Quality scoring (0-100), IQR outliers, ID audit
│   ├── data_cleaning.py        # Deduplication, imputation, winsorization, audit log
│   ├── eda_engine.py           # Standardized Plotly dark SaaS theme & charts
│   ├── healthcare_analytics.py # Amoxicillin AMR phenotyping & co-resistance
│   ├── statistical_analysis.py # Chi2, Cramér's V, ANOVA, descriptives
│   ├── report_generator.py     # Excel workbook & executive HTML report generation
│   └── ui_helper.py            # Consistent sidebar, hero banner, CSS injector
│
├── assets/
│   └── styles.css              # Custom SaaS CSS design system
│
└── outputs/                    # Exported research reports and workbooks
```

---

## 🚀 Installation & Local Execution

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

### 2. Navigate to Project Directory
```powershell
cd "I:\imran\medanalytix"
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Web Application
```powershell
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

---

## 🔒 Privacy & Clinical Governance Protocol

1. **Local Processing Guarantee:** All uploaded data is analyzed exclusively inside local runtime memory. Zero patient health information is transmitted across external networks or third-party AI APIs.
2. **De-Identification Requirement:** Users are instructed to upload de-identified healthcare datasets in compliance with HIPAA, GDPR, and the DPDP Act.
3. **Clinical Research Scope:** This platform is engineered for academic research, hypothesis generation, and healthcare analytics under MCA curriculum guidelines. It does not provide medical diagnosis or therapeutic prescription.

