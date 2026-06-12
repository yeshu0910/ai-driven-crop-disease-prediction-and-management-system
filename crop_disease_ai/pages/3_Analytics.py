import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.translator import t

st.set_page_config(page_title=t("app.title") + " - " + t("nav.analytics"), page_icon="📊", layout="wide")
from utils.translator import init_i18n, t

st.set_page_config(page_title="Analytics - Crop Disease AI", page_icon="📊", layout="wide")


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
            <h1>{t("analytics.title")}</h1>
            <p>{t("analytics.subtitle")}</p>
            <h1>{t('analytics.title')}</h1>
            <p>{t('analytics.subtitle')}</p>
        </div>
    """, unsafe_allow_html=True)


def render_summary_cards(stats):
    cols = st.columns(5)
    metrics = [
        ("🔬", t("stats.total_scans"), stats.get("total_scans", 0), "#2e7d32"),
        ("✅", t("stats.healthy"), stats.get("healthy_scans", 0), "#4caf50"),
        ("⚠️", t("stats.diseased"), stats.get("diseased_scans", 0), "#ff6f00"),
        ("🌾", t("stats.crops_monitored"), stats.get("total_crops", 0), "#1976d2"),
        ("🦠", t("stats.common_disease"), stats.get("most_common_disease", "N/A"), "#e53935")
        ("🔬", t("analytics.stat_total_scans"), stats.get("total_scans", 0), "#2e7d32"),
        ("✅", t("analytics.stat_healthy"), stats.get("healthy_scans", 0), "#4caf50"),
        ("⚠️", t("analytics.stat_diseased"), stats.get("diseased_scans", 0), "#ff6f00"),
        ("🌾", t("analytics.stat_crops_monitored"), stats.get("total_crops", 0), "#1976d2"),
        ("🦠", t("analytics.stat_common_disease"), stats.get("most_common_disease", "N/A"), "#e53935")
    ]
    for i, (icon, label, value, color) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
                <div class="dashboard-card animate-in" style="animation-delay: {i*0.1}s;
                     text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.3rem;">{icon}</div>
                    <div class="card-label">{label}</div>
                    <div class="card-value" style="font-size: 1.4rem; color: {color};">{value}</div>
                </div>
            """, unsafe_allow_html=True)


def render_disease_frequency(db):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.disease_frequency')}</h3>", unsafe_allow_html=True)
    freq_data = db.get_disease_frequency(limit=15)

    if freq_data:
        df = pd.DataFrame(freq_data)
        fig = px.bar(
            df, x="count", y="disease_name",
            orientation="h",
            color="disease_name",
            color_discrete_map={
                d: "#4caf50" if "healthy" in d.lower() else "#ff6f00"
                for d in df["disease_name"]
            },
            template="plotly_white",
            height=500
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title=t("stats.total_scans"),
            xaxis_title=t("analytics.chart_cases"),
            yaxis_title="",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info(t("analytics.no_data"))


def render_monthly_trends(db):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.monthly_trends')}</h3>", unsafe_allow_html=True)
    trends = db.get_monthly_trends(months=12)

    if trends:
        df = pd.DataFrame(trends)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["month"], y=df["total"],
            mode="lines+markers", name=t("stats.total_scans"),
            mode="lines+markers", name=t("analytics.chart_total_scans"),
            line=dict(color="#2e7d32", width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Bar(
            x=df["month"], y=df["healthy"],
            name=t("stats.healthy"), marker_color="#4caf50",
            name=t("analytics.chart_healthy"), marker_color="#4caf50",
            opacity=0.7
        ))
        fig.add_trace(go.Bar(
            x=df["month"], y=df["diseased"],
            name=t("stats.diseased"), marker_color="#ff6f00",
            name=t("analytics.chart_diseased"), marker_color="#ff6f00",
            opacity=0.7
        ))
        fig.update_layout(
            barmode="stack",
            template="plotly_white",
            hovermode="x",
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info(t("analytics.no_trends"))


def render_crop_health_pie(db):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.health_distribution')}</h3>", unsafe_allow_html=True)
        st.info(t("analytics.no_monthly_data"))


def render_crop_health_pie(db):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.crop_health_dist')}</h3>", unsafe_allow_html=True)
    stats = db.get_summary_stats()
    total = stats.get("total_scans", 0)
    healthy = stats.get("healthy_scans", 0)
    diseased = stats.get("diseased_scans", 0)

    if total > 0:
        fig = go.Figure(data=[go.Pie(
            labels=[t("stats.healthy"), t("stats.diseased")],
            labels=[t("analytics.chart_healthy_label"), t("analytics.chart_diseased_label")],
            values=[healthy, diseased],
            marker_colors=["#4caf50", "#ff6f00"],
            textinfo="label+percent",
            hole=0.4,
            pull=[0.05, 0]
        )])
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info(t("analytics.no_health"))
        st.info(t("analytics.no_health_data"))


def render_recent_detections(db):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.recent_detections')}</h3>", unsafe_allow_html=True)
    predictions = db.get_all_predictions(limit=20)

    if predictions:
        data = []
        for p in predictions:
            created = p.get("created_at", "")
            if created and isinstance(created, str) and "T" in created:
                created = created.split(".")[0].replace("T", " ")
            data.append({
                t("common.date"): created or "N/A",
                t("common.crop"): p.get("crop_name", "N/A"),
                t("common.disease"): p.get("disease_name", "N/A"),
                t("common.confidence"): f"{p.get('confidence', 0)*100:.1f}%",
                t("common.severity"): p.get("severity", "N/A"),
                t("common.risk"): p.get("risk_level", "N/A")
                t("analytics.table_date"): created or "N/A",
                t("analytics.table_crop"): p.get("crop_name", "N/A"),
                t("analytics.table_disease"): p.get("disease_name", "N/A"),
                t("analytics.table_confidence"): f"{p.get('confidence', 0)*100:.1f}%",
                t("analytics.table_severity"): p.get("severity", "N/A"),
                t("analytics.table_risk"): p.get("risk_level", "N/A")
            })
        df = pd.DataFrame(data)
        st.dataframe(
            df,
            width='stretch',
            hide_index=True
        )
    else:
        st.info(t("analytics.no_history"))


def render_analytics_overview(db):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.daily_overview')}</h3>", unsafe_allow_html=True)
    analytics_data = db.get_analytics(days=30)

    if analytics_data:
        df = pd.DataFrame(analytics_data)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["total_scans"],
            mode="lines+markers",
            name=t("stats.total_scans"),
            name=t("analytics.chart_total_scans"),
            line=dict(color="#2e7d32", width=2),
            fill="tozeroy",
            fillcolor="rgba(46,125,50,0.1)"
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["healthy_scans"],
            mode="lines+markers",
            name=t("stats.healthy"),
            name=t("analytics.chart_healthy"),
            line=dict(color="#4caf50", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["diseased_scans"],
            mode="lines+markers",
            name=t("stats.diseased"),
            name=t("analytics.chart_diseased"),
            line=dict(color="#ff6f00", width=2)
        ))
        fig.update_layout(
            template="plotly_white",
            hovermode="x",
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info(t("analytics.no_daily"))
        st.info(t("analytics.no_daily_data"))


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    db = get_db()
    stats = db.get_summary_stats()

    render_summary_cards(stats)

    col1, col2 = st.columns([2, 1])
    with col1:
        render_monthly_trends(db)
    with col2:
        render_crop_health_pie(db)

    render_disease_frequency(db)

    col1, col2 = st.columns([1, 1])
    with col1:
        render_analytics_overview(db)
    with col2:
        st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.insights')}</h3>", unsafe_allow_html=True)
        if stats["total_scans"] > 0:
            disease_pct = (stats["diseased_scans"] / stats["total_scans"]) * 100
            healthy_pct = (stats["healthy_scans"] / stats["total_scans"]) * 100

            healthy_label = t("stats.healthy").lower()
            diseased_label = t("stats.diseased").lower()

            st.markdown(f"""
                <div class="dashboard-card">
                    <div class="info-box {'green' if healthy_pct > 50 else 'orange'}">
                        <strong>{t('analytics.crop_health_rate').format(pct=healthy_pct)}</strong><br>
                        <strong>{t('analytics.disease_incidence').format(pct=disease_pct)}</strong>
                    </div>
                    <div class="info-box blue" style="margin-top: 0.5rem;">
                        <strong>{t('analytics.most_common_disease').format(disease=stats.get('most_common_disease', 'N/A'))}</strong><br>
                        <strong>{t('analytics.cases').format(count=stats.get('most_common_count', 0))}</strong>
                    </div>
                    <div class="info-box blue" style="margin-top: 0.5rem;">
                        <strong>{t('analytics.crops_monitored').format(count=stats.get('total_crops', 0))}</strong><br>
                        <strong>{t('analytics.total_entries').format(count=stats['total_scans'])}</strong>
                        <strong>{t('analytics.crop_health_rate', pct=f'{healthy_pct:.1f}')}</strong><br>
                        <strong>{t('analytics.disease_incidence', pct=f'{disease_pct:.1f}')}</strong>
                    </div>
                    <div class="info-box blue" style="margin-top: 0.5rem;">
                        <strong>{t('analytics.most_common_disease', disease=stats.get('most_common_disease', 'N/A'))}</strong><br>
                        <strong>{t('analytics.cases', count=stats.get('most_common_count', 0))}</strong>
                    </div>
                    <div class="info-box blue" style="margin-top: 0.5rem;">
                        <strong>{t('analytics.crops_monitored', count=stats.get('total_crops', 0))}</strong><br>
                        <strong>{t('analytics.total_entries', count=stats['total_scans'])}</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info(t("analytics.no_insights"))

    render_recent_detections(db)

    if st.button(t("analytics.btn_refresh"), type="primary", width='stretch'):
        st.rerun()


if __name__ == "__main__":
    main()
