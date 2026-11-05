import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing MEDANALYTIX backend imports...")
import modules.data_loader as dl
import modules.data_quality as dq
import modules.data_cleaning as dc
import modules.eda_engine as ee
import modules.healthcare_analytics as ha
import modules.statistical_analysis as sa
import modules.report_generator as rg
import modules.ui_helper as uh

print("[OK] All 8 modules imported successfully.")

df, err = dl.load_research_benchmark_dataset()
assert df is not None, f"Failed loading benchmark: {err}"
print(f"[OK] Benchmark dataset loaded: shape = {df.shape}")

meta = dl.extract_metadata(df, filename="amoxicillin_resistance_tracking.csv", file_size_bytes=233181)
print(f"[OK] Metadata extracted: {meta['rows']} rows, {meta['columns']} cols, is_amr = {meta['is_amoxicillin_research']}")

score, grade, breakdown = dq.calculate_data_quality_score(df)
print(f"[OK] Quality Score: {score}/100 ({grade})")

col_summary = dq.compute_column_quality_summary(df)
print(f"[OK] Column Quality Matrix: {len(col_summary)} features profiled.")

amox_counts, amox_fig = ha.analyze_amoxicillin_distribution(df)
print(f"[OK] Amoxicillin Phenotypes: {len(amox_counts)} clinical categories (Sensitive, Intermediate, Resistant).")
assert len(amox_counts) == 3, "Error: Must preserve all 3 categories!"

descriptives = sa.compute_numerical_descriptives(df)
print(f"[OK] Descriptive Statistics: {len(descriptives)} continuous variables.")

chi_res = sa.run_chi_square_test(df, "Specimen_Type", "Amoxicillin")
print(f"[OK] Chi-Square Test: chi2 = {chi_res['chi2_statistic']}, p = {chi_res['p_value']}, Cramers V = {chi_res['cramers_v']}")

excel_bytes = rg.generate_multi_sheet_excel(df, meta, col_summary, [], descriptives, amox_counts)
print(f"[OK] Multi-Sheet Excel Workbook: {len(excel_bytes):,} bytes generated.")

html_report = rg.generate_executive_html_report(df, meta, col_summary, [], descriptives, score, grade, amox_counts)
print(f"[OK] Executive HTML Report: {len(html_report):,} characters generated.")

# Test cleaning operations
clean_dedup, d_log = dc.remove_duplicate_rows(df)
print(f"[OK] Deduplication engine: {d_log['details']}")

clean_txt, t_logs = dc.standardize_text_columns(df, ["Specimen_Type"], strip_whitespace=True, case_style="Title Case")
print(f"[OK] Text standardization engine: {len(t_logs)} operations logged.")

print("\n=======================================================")
print(" ALL MEDANALYTIX BACKEND VERIFICATION TESTS PASSED!    ")
print("=======================================================")
