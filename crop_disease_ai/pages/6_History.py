import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.translator import init_i18n, t

st.set_page_config(page_title="History - Crop Disease AI", page_icon="📋", layout="wide")


def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_db():
    from database.db_manager import DatabaseManager
    return DatabaseManager()


def render_header():
    st.markdown(f"""
        <div class="main-header">
            <h1>{t('history.title')}</h1>
            <p>{t('history.subtitle')}</p>
        </div>
    """, unsafe_allow_html=True)


def render_filters():
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input(t("history.search_label"), placeholder=t("history.search_placeholder"))
    with col2:
        sort_by = st.selectbox(t("history.sort_label"), [t("history.sort_newest"), t("history.sort_oldest"), t("history.sort_highest_conf"), t("history.sort_lowest_conf")])
    with col3:
        filter_crop = st.text_input(t("history.filter_label"), placeholder=t("history.filter_placeholder"))
    return search, sort_by, filter_crop


def render_predictions_table(predictions, search_query, sort_by, crop_filter):
    if not predictions:
        st.info(t("history.no_records"))
        return

    data = []
    for p in predictions:
        created = p.get("created_at", "")
        if created and isinstance(created, str) and "T" in created:
            created = created.split(".")[0].replace("T", " ")

        item = {
            "id": p.get("id"),
            t("history.table_date"): created or "N/A",
            t("history.table_crop"): p.get("crop_name", "N/A"),
            t("history.table_disease"): p.get("disease_name", "N/A"),
            "Confidence": p.get("confidence", 0),
            t("history.table_severity"): p.get("severity", "N/A"),
            t("history.table_risk"): p.get("risk_level", "N/A"),
            t("history.table_farmer"): p.get("farmer_name", "N/A")
        }
        data.append(item)

    df = pd.DataFrame(data)

    if search_query:
        mask = (
            df[t("history.table_disease")].str.contains(search_query, case=False, na=False) |
            df[t("history.table_crop")].str.contains(search_query, case=False, na=False)
        )
        df = df[mask]

    if crop_filter:
        df = df[df[t("history.table_crop")].str.contains(crop_filter, case=False, na=False)]

    sort_col = t("history.table_date")
    if sort_by == t("history.sort_newest"):
        df = df.sort_values(sort_col, ascending=False)
    elif sort_by == t("history.sort_oldest"):
        df = df.sort_values(sort_col, ascending=True)
    elif sort_by == t("history.sort_highest_conf"):
        df = df.sort_values("Confidence", ascending=False)
    elif sort_by == t("history.sort_lowest_conf"):
        df = df.sort_values("Confidence", ascending=True)

    st.markdown(f"<p style='color: #888;'>{t('history.showing_records', count=len(df))}</p>", unsafe_allow_html=True)

    for _, row in df.iterrows():
        confidence_pct = row["Confidence"] * 100 if isinstance(row["Confidence"], float) else row["Confidence"]
        severity = str(row[t("history.table_severity")])
        sev_color = {"Healthy": "#4caf50", "Mild": "#f1c40f", "Moderate": "#e67e22", "Severe": "#e53935"}.get(severity, "#888")

        st.markdown(f"""
            <div class="metric-card" style="border-left-color: {sev_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 1.1rem;">{row[t('history.table_crop')]}</strong> — {row[t('history.table_disease')]}
                    </div>
                    <span class="badge badge-{'green' if severity=='Healthy' or severity=='Mild' else 'orange' if severity=='Moderate' else 'red'}">
                        {severity}
                    </span>
                </div>
                <div style="display: flex; gap: 2rem; margin-top: 0.5rem; font-size: 0.85rem; color: #666;">
                    <span>📅 {row[t('history.table_date')]}</span>
                    <span>🎯 {t('history.label_confidence', pct=f'{confidence_pct:.1f}')}</span>
                    <span>⚠️ {t('history.label_risk', risk=row[t('history.table_risk')])}</span>
                    <span>👤 {row[t('history.table_farmer')]}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    return df


def render_delete_options(predictions):
    st.markdown("---")
    with st.expander(t("history.manage_records")):
        if predictions:
            delete_id = st.number_input(t("history.delete_id"), min_value=1, step=1)
            if st.button(t("history.btn_delete"), type="secondary", width='stretch'):
                st.warning(t("history.delete_unavailable"))


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    db = get_db()
    search_query, sort_by, crop_filter = render_filters()
    predictions = db.get_all_predictions(limit=200)
    render_predictions_table(predictions, search_query, sort_by, crop_filter)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(t("history.btn_refresh"), width='stretch'):
            st.rerun()
    with col2:
        if predictions and st.button(t("history.btn_export_csv"), width='stretch'):
            data = []
            for p in predictions:
                data.append({
                    "ID": p.get("id"),
                    "Date": p.get("created_at"),
                    "Crop": p.get("crop_name"),
                    "Disease": p.get("disease_name"),
                    "Confidence": p.get("confidence"),
                    "Severity": p.get("severity"),
                    "Risk": p.get("risk_level"),
                    "Farmer": p.get("farmer_name")
                })
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            st.download_button(
                label=t("history.btn_download_csv"),
                data=csv,
                file_name=f"disease_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch'
            )
    with col3:
        st.markdown("")


if __name__ == "__main__":
    main()
