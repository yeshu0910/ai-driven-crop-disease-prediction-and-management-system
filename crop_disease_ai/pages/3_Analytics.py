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
        <div class="main-header">
            <h1>{t("analytics.title")}</h1>
            <p>{t("analytics.subtitle")}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def has_data(stats):
    """Return True if there is any scan data to report on."""
    return stats.get("total_scans", 0) > 0


def render_empty_state():
    """Show a friendly banner when no prediction data exists yet."""
    st.info(
        "📊 **No prediction data available yet.** "
        "Please run a detection first on the **Disease Detection** page. "
        "Once you have results, this dashboard will display your analytics "
        "and visualisations."
    )


def render_summary_cards(stats):
    """Render KPI metric cards — each uses st.metric for a clean look."""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            label=t("stats.total_scans"),
            value=stats.get("total_scans", 0),
            delta=None,
        )
    with col2:
        st.metric(
            label=t("stats.healthy"),
            value=stats.get("healthy_scans", 0),
            delta=None,
        )
    with col3:
        st.metric(
            label=t("stats.diseased"),
            value=stats.get("diseased_scans", 0),
            delta=None,
        )
    with col4:
        st.metric(
            label=t("stats.crops_monitored"),
            value=stats.get("total_crops", 0),
            delta=None,
        )
    with col5:
        common = stats.get("most_common_disease", "N/A")
        st.metric(
            label=t("stats.common_disease"),
            value=common if len(str(common)) < 18 else common[:15] + "…",
            delta=None,
        )


def render_disease_frequency(db):
    """Bar chart of disease frequency (most common first)."""
    st.markdown(
        f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.disease_frequency')}</h3>",
        unsafe_allow_html=True,
    )
    try:
        freq_data = db.get_disease_frequency(limit=15)
    except Exception:
        freq_data = []

    if not freq_data:
        st.info(t("analytics.no_data"))
        return

    df = pd.DataFrame(freq_data)
    fig = px.bar(
        df,
        x="count",
        y="disease_name",
        orientation="h",
        color="disease_name",
        color_discrete_map={
            d: "#4caf50" if "healthy" in d.lower() else "#ff6f00"
            for d in df["disease_name"]
        },
        template="plotly_white",
        height=500,
    )
    fig.update_layout(
        showlegend=False,
        xaxis_title=t("analytics.chart_cases"),
        yaxis_title="",
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, width="stretch")


def render_monthly_trends(db):
    """Line + bar chart showing monthly scan trends."""
    st.markdown(
        f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.monthly_trends')}</h3>",
        unsafe_allow_html=True,
    )
    try:
        trends = db.get_monthly_trends(months=12)
    except Exception:
        trends = []

    if not trends:
        st.info(t("analytics.no_trends"))
        return

    df = pd.DataFrame(trends)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["month"],
            y=df["total"],
            mode="lines+markers",
            name=t("analytics.chart_total_scans"),
            line={"color": "#2e7d32", "width": 3},
            marker={"size": 8},
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["month"],
            y=df["healthy"],
            name=t("analytics.chart_healthy"),
            marker_color="#4caf50",
            opacity=0.7,
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["month"],
            y=df["diseased"],
            name=t("analytics.chart_diseased"),
            marker_color="#ff6f00",
            opacity=0.7,
        )
    )
    fig.update_layout(
        barmode="stack",
        template="plotly_white",
        hovermode="x",
        height=400,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        legend={"orientation": "h", "y": 1.1},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


def render_crop_health_pie(stats):
    """Donut chart showing healthy vs diseased proportions."""
    st.markdown(
        f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.crop_health_dist')}</h3>",
        unsafe_allow_html=True,
    )
    total = stats.get("total_scans", 0)
    healthy = stats.get("healthy_scans", 0)
    diseased = stats.get("diseased_scans", 0)

    if total == 0:
        st.info(t("analytics.no_health_data"))
        return

    fig = go.Figure(
        data=[
            go.Pie(
                labels=[
                    t("analytics.chart_healthy_label"),
                    t("analytics.chart_diseased_label"),
                ],
                values=[healthy, diseased],
                marker_colors=["#4caf50", "#ff6f00"],
                textinfo="label+percent",
                hole=0.4,
                pull=[0.05, 0],
            )
        ]
    )
    fig.update_layout(
        height=350,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        showlegend=True,
        legend={"orientation": "h", "y": 1.1},
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


def render_daily_overview(db):
    """Daily scan overview line chart."""
    st.markdown(
        f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.daily_overview')}</h3>",
        unsafe_allow_html=True,
    )
    try:
        analytics_data = db.get_analytics(days=30)
    except Exception:
        analytics_data = []

    if not analytics_data:
        st.info(t("analytics.no_daily_data"))
        return

    df = pd.DataFrame(analytics_data)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["total_scans"],
            mode="lines+markers",
            name=t("analytics.chart_total_scans"),
            line={"color": "#2e7d32", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(46,125,50,0.1)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["healthy_scans"],
            mode="lines+markers",
            name=t("analytics.chart_healthy"),
            line={"color": "#4caf50", "width": 2},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["diseased_scans"],
            mode="lines+markers",
            name=t("analytics.chart_diseased"),
            line={"color": "#ff6f00", "width": 2},
        )
    )
    fig.update_layout(
        template="plotly_white",
        hovermode="x",
        height=350,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        legend={"orientation": "h", "y": 1.1},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


def render_insights_panel(stats):
    """Show computed analytical insights from the data."""
    st.markdown(
        f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.insights')}</h3>",
        unsafe_allow_html=True,
    )
    total = stats["total_scans"]
    healthy = stats["healthy_scans"]
    diseased = stats["diseased_scans"]
    disease_pct = (diseased / total) * 100
    healthy_pct = (healthy / total) * 100

    st.markdown(
        f"""
        <div class="card">
            <div class="info-box {'green' if healthy_pct > 50 else 'orange'}">
                <strong>{t('analytics.crop_health_rate', pct=f'{healthy_pct:.1f}')}</strong><br>
                <strong>{t('analytics.disease_incidence', pct=f'{disease_pct:.1f}')}</strong>
            </div>
            <div class="info-box blue" style="margin-top: 0.5rem;">
                <strong>{t('analytics.most_common_disease', disease=stats.get('most_common_disease', 'N/A'))}</strong><br>
                <strong>{t('analytics.cases', count=stats.get('most_common_count', 0))}</strong>
            </div>
            <div class="info-box blue" style="margin-top: 0.5rem;">
                <strong>{t('analytics.crops_monitored', count=stats.get('total_crops', 0))}</strong><br>
                <strong>{t('analytics.total_entries', count=total)}</strong>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_recent_detections_table(db):
    """Render a table of the most recent predictions."""
    st.markdown(
        f"<h3 style='margin: 1.5rem 0 1rem;'>{t('analytics.recent_detections')}</h3>",
        unsafe_allow_html=True,
    )
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
        records.append(
            {
                t("common.date"): created or "N/A",
                t("common.crop"): p.get("crop_name", "N/A"),
                t("common.disease"): p.get("disease_name", "N/A"),
                t("common.confidence"): f"{p.get('confidence', 0) * 100:.1f}%",
                t("common.severity"): p.get("severity", "N/A"),
                t("common.risk"): p.get("risk_level", "N/A"),
            }
        )

    df = pd.DataFrame(records)
    st.dataframe(df, width="stretch", hide_index=True)


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    # ── Fetch data (with defensive error handling) ──
    try:
        db = get_db()
        stats = db.get_summary_stats()
    except Exception:
        st.error("Failed to connect to the database. Some features may be unavailable.")
        stats = {
            "total_scans": 0,
            "healthy_scans": 0,
            "diseased_scans": 0,
            "total_crops": 0,
            "most_common_disease": "N/A",
            "most_common_count": 0,
        }

    # ── Empty-state guard ──
    if not has_data(stats):
        render_empty_state()
        return

    # ── KPI Cards ──
    render_summary_cards(stats)

    # ── Row 1: Monthly trends + Crop health pie ──
    col1, col2 = st.columns([2, 1])
    with col1:
        render_monthly_trends(db)
    with col2:
        render_crop_health_pie(stats)

    # ── Row 2: Disease frequency bar chart ──
    render_disease_frequency(db)

    # ── Row 3: Daily overview + Insights ──
    col1, col2 = st.columns([1, 1])
    with col1:
        render_daily_overview(db)
    with col2:
        render_insights_panel(stats)

    # ── Row 4: Recent detections table ──
    render_recent_detections_table(db)

    # ── Manual refresh button ──
    if st.button(t("analytics.btn_refresh"), type="primary", width="stretch"):
        st.rerun()


if __name__ == "__main__":
    main()