import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.translator import init_i18n, t

st.set_page_config(
    page_title=t("app.title") + " - " + t("nav.analytics"),
    page_icon="📊",
    layout="wide",
)


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_db():
    from database.db_manager import DatabaseManager
    return DatabaseManager()


def render_header():
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{t("analytics.title")}</h1>
            <p>{t("analytics.subtitle")}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def has_data(stats):
    return stats.get("total_scans", 0) > 0


def render_empty_state():
    st.markdown(
        """
        <div class="card" style="padding:2rem;text-align:center;margin:2rem 0;">
            <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
            <h3 style="font-weight:700;margin-bottom:0.5rem;color:var(--text);">No prediction data available yet</h3>
            <p style="color:var(--text-secondary);">Please run a detection first on the <strong>Disease Detection</strong> page.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_cards(stats):
    from app import render_metric_card
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card(t("stats.total_scans"), stats.get("total_scans", 0), icon="🔬", color="var(--primary)")
    with col2:
        render_metric_card(t("stats.healthy"), stats.get("healthy_scans", 0), icon="✅", color="var(--success)")
    with col3:
        render_metric_card(t("stats.diseased"), stats.get("diseased_scans", 0), icon="⚠️", color="var(--warning)")
    with col4:
        render_metric_card(t("stats.crops_monitored"), stats.get("total_crops", 0), icon="🌾", color="var(--info)")
    with col5:
        common = stats.get("most_common_disease", "N/A")
        render_metric_card(t("stats.common_disease"), common[:18] + "…" if len(str(common)) >= 18 else common, icon="🦠", color="var(--accent)")


def render_disease_frequency(db):
    st.markdown(f"<h3 style='margin:1.5rem 0 1rem;font-size:1.05rem;font-weight:700;'>{t('analytics.disease_frequency')}</h3>", unsafe_allow_html=True)
    try:
        freq_data = db.get_disease_frequency(limit=15)
    except Exception:
        freq_data = []
    if not freq_data:
        st.info(t("analytics.no_data"))
        return
    df = pd.DataFrame(freq_data)
    fig = px.bar(df, x="count", y="disease_name", orientation="h", color="disease_name",
                 color_discrete_map={d: "#22C55E" if "healthy" in d.lower() else "#F59E0B" for d in df["disease_name"]},
                 template="plotly_dark", height=500)
    fig.update_layout(showlegend=False, xaxis_title=t("analytics.chart_cases"), yaxis_title="",
                      margin={"l": 10, "r": 10, "t": 10, "b": 10},
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font={"color": "#94A3B8"}, xaxis={"gridcolor": "rgba(148,163,184,0.1)"},
                      yaxis={"gridcolor": "rgba(148,163,184,0.1)"})
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, width="stretch")


def render_monthly_trends(db):
    st.markdown(f"<h3 style='margin:1.5rem 0 1rem;font-size:1.05rem;font-weight:700;'>{t('analytics.monthly_trends')}</h3>", unsafe_allow_html=True)
    try:
        trends = db.get_monthly_trends(months=12)
    except Exception:
        trends = []
    if not trends:
        st.info(t("analytics.no_trends"))
        return
    df = pd.DataFrame(trends)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["month"], y=df["total"], mode="lines+markers", name=t("analytics.chart_total_scans"),
                              line={"color": "#22C55E", "width": 3}, marker={"size": 8, "color": "#22C55E"}))
    fig.add_trace(go.Bar(x=df["month"], y=df["healthy"], name=t("analytics.chart_healthy"), marker_color="#16A34A", opacity=0.7))
    fig.add_trace(go.Bar(x=df["month"], y=df["diseased"], name=t("analytics.chart_diseased"), marker_color="#F59E0B", opacity=0.7))
    fig.update_layout(barmode="stack", template="plotly_dark", hovermode="x", height=400,
                      margin={"l": 10, "r": 10, "t": 10, "b": 10},
                      legend={"orientation": "h", "y": 1.1, "font": {"color": "#94A3B8"}},
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font={"color": "#94A3B8"}, xaxis={"gridcolor": "rgba(148,163,184,0.1)", "showgrid": False},
                      yaxis={"gridcolor": "rgba(148,163,184,0.1)"})
    st.plotly_chart(fig, width="stretch")


def render_crop_health_pie(stats):
    st.markdown(f"<h3 style='margin:1.5rem 0 1rem;font-size:1.05rem;font-weight:700;'>{t('analytics.crop_health_dist')}</h3>", unsafe_allow_html=True)
    total = stats.get("total_scans", 0)
    healthy = stats.get("healthy_scans", 0)
    diseased = stats.get("diseased_scans", 0)
    if total == 0:
        st.info(t("analytics.no_health_data"))
        return
    fig = go.Figure(data=[go.Pie(labels=[t("analytics.chart_healthy_label"), t("analytics.chart_diseased_label")],
                                  values=[healthy, diseased], marker_colors=["#22C55E", "#F59E0B"],
                                  textinfo="label+percent", textfont_color="#F8FAFC", hole=0.4, pull=[0.05, 0])])
    fig.update_layout(height=350, margin={"l": 10, "r": 10, "t": 10, "b": 10},
                      showlegend=True, legend={"orientation": "h", "y": 1.1, "font": {"color": "#94A3B8"}},
                      paper_bgcolor="rgba(0,0,0,0)", font={"color": "#94A3B8"})
    st.plotly_chart(fig, width="stretch")


def render_daily_overview(db):
    st.markdown(f"<h3 style='margin:1.5rem 0 1rem;font-size:1.05rem;font-weight:700;'>{t('analytics.daily_overview')}</h3>", unsafe_allow_html=True)
    try:
        analytics_data = db.get_analytics(days=30)
    except Exception:
        analytics_data = []
    if not analytics_data:
        st.info(t("analytics.no_daily_data"))
        return
    df = pd.DataFrame(analytics_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["total_scans"], mode="lines+markers", name=t("analytics.chart_total_scans"),
                              line={"color": "#22C55E", "width": 2}, fill="tozeroy", fillcolor="rgba(34,197,94,0.1)"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["healthy_scans"], mode="lines+markers", name=t("analytics.chart_healthy"),
                              line={"color": "#16A34A", "width": 2}))
    fig.add_trace(go.Scatter(x=df["date"], y=df["diseased_scans"], mode="lines+markers", name=t("analytics.chart_diseased"),
                              line={"color": "#F59E0B", "width": 2}))
    fig.update_layout(template="plotly_dark", hovermode="x", height=350, margin={"l": 10, "r": 10, "t": 10, "b": 10},
                      legend={"orientation": "h", "y": 1.1, "font": {"color": "#94A3B8"}},
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font={"color": "#94A3B8"}, xaxis={"gridcolor": "rgba(148,163,184,0.1)", "showgrid": False},
                      yaxis={"gridcolor": "rgba(148,163,184,0.1)"})
    st.plotly_chart(fig, width="stretch")


def render_insights_panel(stats):
    st.markdown(f"<h3 style='margin:1.5rem 0 1rem;font-size:1.05rem;font-weight:700;'>{t('analytics.insights')}</h3>", unsafe_allow_html=True)
    total = stats["total_scans"]
    healthy = stats["healthy_scans"]
    diseased = stats["diseased_scans"]
    disease_pct = round((diseased / total) * 100, 1) if total > 0 else 0
    healthy_pct = round((healthy / total) * 100, 1) if total > 0 else 100
    st.markdown(
        f"""
        <div class="card">
            <div class="info-box {"green" if healthy_pct > 50 else "orange"}">
                <strong>{t("analytics.crop_health_rate", pct=f"{healthy_pct:.1f}")}</strong><br>
                <strong>{t("analytics.disease_incidence", pct=f"{disease_pct:.1f}")}</strong>
            </div>
            <div class="info-box blue" style="margin-top: 0.5rem;">
                <strong>{t("analytics.most_common_disease", disease=stats.get("most_common_disease", "N/A"))}</strong><br>
                <strong>{t("analytics.cases", count=stats.get("most_common_count", 0))}</strong>
            </div>
            <div class="info-box blue" style="margin-top: 0.5rem;">
                <strong>{t("analytics.crops_monitored", count=stats.get("total_crops", 0))}</strong><br>
                <strong>{t("analytics.total_entries", count=total)}</strong>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)


def render_recent_detections_table(db):
    st.markdown(f"<h3 style='margin:1.5rem 0 1rem;font-size:1.05rem;font-weight:700;'>{t('analytics.recent_detections')}</h3>", unsafe_allow_html=True)
    try:
        predictions = db.get_all_predictions(limit=20)
    except Exception:
        predictions = []
    if not predictions:
        st.info(t("analytics.no_history"))
        return
    records = []
    for p in predictions:
        created = p.get("created_at", "")
        if created and isinstance(created, str) and "T" in created:
            created = created.split(".")[0].replace("T", " ")
        records.append({t("common.date"): created or "N/A", t("common.crop"): p.get("crop_name", "N/A"),
                        t("common.disease"): p.get("disease_name", "N/A"),
                        t("common.confidence"): f"{p.get('confidence', 0) * 100:.1f}%",
                        t("common.severity"): p.get("severity", "N/A"), t("common.risk"): p.get("risk_level", "N/A")})
    st.dataframe(pd.DataFrame(records), width="stretch", hide_index=True)


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()
    try:
        db = get_db()
        stats = db.get_summary_stats()
    except Exception:
        st.error("Failed to connect to the database. Some features may be unavailable.")
        stats = {"total_scans": 0, "healthy_scans": 0, "diseased_scans": 0, "total_crops": 0,
                 "most_common_disease": "N/A", "most_common_count": 0}
    if not has_data(stats):
        render_empty_state()
        return
    render_summary_cards(stats)
    col1, col2 = st.columns([2, 1])
    with col1:
        render_monthly_trends(db)
    with col2:
        render_crop_health_pie(stats)
    render_disease_frequency(db)
    col1, col2 = st.columns([1, 1])
    with col1:
        render_daily_overview(db)
    with col2:
        render_insights_panel(stats)
    render_recent_detections_table(db)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(t("analytics.btn_refresh"), type="primary", width="stretch"):
        st.rerun()


if __name__ == "__main__":
    main()
