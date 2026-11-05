"""
modules/ui_helper.py
--------------------
Shared UI components and styling injector for all MEDANALYTIX pages.
"""

import os
import streamlit as st
import pandas as pd
from modules.data_loader import (
    load_research_benchmark_dataset,
    initialize_session_dataset,
    get_active_dataset
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
CSS_PATH = os.path.join(ASSETS_DIR, "styles.css")


def inject_custom_css():
    """Injects the master MEDANALYTIX stylesheet into the active Streamlit DOM."""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_sidebar():
    """Renders the consistent MEDANALYTIX sidebar branding and dataset status."""
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 18px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 16px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size: 1.8rem; filter: drop-shadow(0 0 10px #ff0055);">🧬</span>
                <div>
                    <div style="font-size: 1.35rem; font-weight: 800; background: linear-gradient(135deg, #ff0055 0%, #ff6b00 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">MEDANALYTIX</div>
                    <div style="font-size: 0.72rem; color: #cbd5e1; letter-spacing: 0.05em; text-transform: uppercase;">Healthcare Data Intelligence</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        active_df, metadata = get_active_dataset()

        st.markdown("<p style='font-size:0.75rem; text-transform:uppercase; color:#94a3b8; font-weight:700; margin-bottom:6px;'>Active Dataset Status</p>", unsafe_allow_html=True)

        if active_df is not None and metadata is not None:
            is_res = metadata.get("is_amoxicillin_research", False)
            badge_html = "<span class='badge-red'>AMR Research Dataset</span>" if is_res else "<span class='badge-coral'>General Healthcare</span>"
            st.markdown(f"""
            <div style="background: rgba(20, 10, 18, 0.85); border: 1px solid rgba(255, 0, 85, 0.35); border-radius: 10px; padding: 12px; margin-bottom: 14px; box-shadow: 0 0 16px rgba(255, 0, 85, 0.1);">
                <div style="font-size: 0.88rem; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    📄 {metadata.get('filename', 'dataset.csv')}
                </div>
                <div style="font-size: 0.78rem; color: #cbd5e1; margin: 4px 0 8px 0;">
                    <b>{metadata.get('rows', 0):,}</b> rows &bull; <b>{metadata.get('columns', 0)}</b> cols
                </div>
                {badge_html}
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Reset to Original Data", use_container_width=True):
                raw_df = st.session_state.get("raw_df", None)
                if raw_df is not None:
                    st.session_state["active_df"] = raw_df.copy()
                    st.session_state["cleaned_df"] = raw_df.copy()
                    st.session_state["cleaning_log"] = []
                    st.success("Dataset reset to original upload state!")
                    st.rerun()

        else:
            st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.5); border: 1px dashed rgba(255,255,255,0.15); border-radius: 10px; padding: 14px; text-align: center; margin-bottom: 14px;">
                <div style="font-size: 1.2rem; margin-bottom: 4px;">📂</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">No dataset currently loaded</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("⚡ Load MCA Research Dataset", use_container_width=True):
                df_sample, err = load_research_benchmark_dataset()
                if df_sample is not None:
                    initialize_session_dataset(df_sample, filename="amoxicillin_resistance_tracking.csv", file_size_bytes=233181)
                    st.success("Loaded MCA Amoxicillin Research Dataset (2,200 isolates)!")
                    st.rerun()
                else:
                    st.error(f"Could not load local dataset: {err}")

        st.markdown("""
        <div style="margin-top: 24px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.75rem; color: #64748b;">
            <b>MCA Analytics Framework</b><br>
            CLSI / EUCAST Protocol Alignment<br>
            Secure Local Computation
        </div>
        """, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, tag: str = "Healthcare Analytics Platform"):
    """Renders a sleek, SaaS-grade hero header for every page."""
    st.markdown(f"""
    <div class="med-hero">
        <div class="med-tag">{tag}</div>
        <div class="med-title">{title}</div>
        <div class="med-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def check_dataset_or_warn() -> tuple[pd.DataFrame | None, dict | None]:
    """Helper that verifies if a dataset is loaded; if not, renders an empty-state guidance card."""
    active_df, metadata = get_active_dataset()
    if active_df is None:
        st.markdown("""
        <div class="med-card" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">📊</div>
            <h3 style="color: #ffffff; margin-bottom: 8px;">No Dataset Loaded</h3>
            <p style="color: #94a3b8; max-width: 520px; margin: 0 auto 24px auto; font-size: 0.95rem;">
                Please upload a CSV or Excel file in the <b>Dataset Upload</b> module, or click below to immediately load the MCA Research Dataset for demonstration.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⚡ Quick-Load MCA Amoxicillin Research Dataset", use_container_width=True):
                df_sample, err = load_research_benchmark_dataset()
                if df_sample is not None:
                    initialize_session_dataset(df_sample, filename="amoxicillin_resistance_tracking.csv", file_size_bytes=233181)
                    st.success("Loaded MCA Research Dataset successfully!")
                    st.rerun()
                else:
                    st.error(f"Error loading benchmark: {err}")
        return None, None

    return active_df, metadata

