import random  # nosec: demo chart data only
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.translator import init_i18n, t

st.set_page_config(
    page_title=t("app.title") + " - " + t("nav.home"), page_icon="🌱", layout="wide"
)


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header():
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{t("home.title")}</h1>
            <p>{t("home.subtitle")}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_stat_cards(stats):
    cols = st.columns(4)
    icons = ["🔬", "✅", "⚠️", "📊"]
    labels = [
        t("stats.total_scans"),
        t("stats.healthy_crops"),
        t("stats.diseases_found"),
        t("stats.crops_monitored"),
    ]
    colors = ["#22C55E", "#16A34A", "#F59E0B", "#3B82F6"]

    for i, (col, icon, label, color) in enumerate(
        zip(cols, icons, labels, colors, strict=False)
    ):
        value = list(stats.values())[i] if i < len(stats) else 0
        col.markdown(
            f"""
            <div class="stat-card animate-in animate-delay-{i}" style="animation-delay:{i * 0.1}s">
                <div style="width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;
                     font-size:1.4rem;margin:0 auto 0.75rem;background:{color}15;border:1px solid {color}30;">{icon}</div>
                <div class="card-label">{label}</div>
                <div class="card-value">{value}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )


def render_features():
    st.markdown(
        f"<h2 style='margin:2rem 0 1.5rem;font-weight:700;font-size:1.1rem;'>{t('home.core_capabilities')}</h2>",
        unsafe_allow_html=True,
    )

    features = [
        {
            "icon": "🧠",
            "title": t("home.feature_ai_title"),
            "desc": t("home.feature_ai_desc"),
        },
        {
            "icon": "🌡️",
            "title": t("home.feature_weather_title"),
            "desc": t("home.feature_weather_desc"),
        },
        {
            "icon": "💊",
            "title": t("home.feature_treatment_title"),
            "desc": t("home.feature_treatment_desc"),
        },
        {
            "icon": "📊",
            "title": t("home.feature_analytics_title"),
            "desc": t("home.feature_analytics_desc"),
        },
        {
            "icon": "📄",
            "title": t("home.feature_pdf_title"),
            "desc": t("home.feature_pdf_desc"),
        },
        {
            "icon": "🔍",
            "title": t("home.feature_xai_title"),
            "desc": t("home.feature_xai_desc"),
        },
    ]
    for feat in features:
        st.markdown(
            f"""
            <div class="glow-card feature-card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:2.2rem;margin-bottom:0.5rem;">{feat["icon"]}</div>
                <h3 style="font-size:1rem;font-weight:700;margin-bottom:0.4rem;color:var(--text);">{feat["title"]}</h3>
                <p style="color:var(--text-secondary);font-size:0.85rem;line-height:1.5;">{feat["desc"]}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_supported_crops():
    crops = [
        ("Tomato", "🍅"),
        ("Potato", "🥔"),
        ("Rice", "🌾"),
        ("Wheat", "🌾"),
        ("Corn", "🌽"),
        ("Cotton", "🌿"),
        ("Soybean", "🫘"),
        ("Sugarcane", "🎋"),
        ("Groundnut", "🥜"),
        ("Sunflower", "🌻"),
        ("Banana", "🍌"),
        ("Mango", "🥭"),
        ("Grapes", "🍇"),
        ("Apple", "🍎"),
        ("Chili", "🌶️"),
    ]

    st.markdown(
        f"<h2 style='margin:2rem 0 1.5rem;font-weight:700;font-size:1.1rem;'>{t('home.supported_crops')}</h2>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="crop-grid">', unsafe_allow_html=True)
    for crop, emoji in crops:
        st.markdown(
            f"""
            <div class="crop-item">
                <div class="crop-emoji">{emoji}</div>
                <div class="crop-name">{crop}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_workflow():
    st.markdown(
        f"<h2 style='margin:2rem 0 1.5rem;font-weight:700;font-size:1.1rem;'>{t('home.how_it_works')}</h2>",
        unsafe_allow_html=True,
    )

    steps = [
        ("1", t("home.step1_title"), t("home.step1_desc")),
        ("2", t("home.step2_title"), t("home.step2_desc")),
        ("3", t("home.step3_title"), t("home.step3_desc")),
        ("4", t("home.step4_title"), t("home.step4_desc")),
        ("5", t("home.step5_title"), t("home.step5_desc")),
        ("6", t("home.step6_title"), t("home.step6_desc")),
    ]
    st.markdown('<div class="workflow-grid">', unsafe_allow_html=True)
    for num, title, desc in steps:
        st.markdown(
            f"""
            <div class="workflow-step">
                <div class="step-number">{num}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_quick_stats_chart():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    healthy_vals = [random.randint(10, 30) for _ in range(6)]  # nosec: demo chart data
    diseased_vals = [random.randint(5, 20) for _ in range(6)]  # nosec: demo chart data

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name=t("home.chart_healthy"),
            x=months,
            y=healthy_vals,
            marker_color="#22C55E",
            text=healthy_vals,
            textposition="auto",
            textfont_color="#F8FAFC",
        )
    )
    fig.add_trace(
        go.Bar(
            name=t("home.chart_diseased"),
            x=months,
            y=diseased_vals,
            marker_color="#F59E0B",
            text=diseased_vals,
            textposition="auto",
            textfont_color="#F8FAFC",
        )
    )
    fig.update_layout(
        barmode="group",
        title=t("home.chart_monthly_trends"),
        title_font_color="#F8FAFC",
        template="plotly_dark",
        hovermode="x",
        height=350,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        legend={"orientation": "h", "y": 1.1, "font": {"color": "#94A3B8"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#94A3B8"},
        xaxis={"gridcolor": "rgba(148,163,184,0.1)", "showgrid": False},
        yaxis={"gridcolor": "rgba(148,163,184,0.1)"},
    )
    st.plotly_chart(fig, width="stretch")


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    try:
        from database.db_manager import DatabaseManager

        db = DatabaseManager()
        stats = db.get_summary_stats()
    except Exception:
        stats = {
            "total_scans": 0,
            "healthy_scans": 0,
            "diseased_scans": 0,
            "total_crops": 15,
            "most_common_disease": "N/A",
        }

    if stats["total_scans"] == 0:
        stats = {
            "total_scans": 0,
            "healthy_scans": 0,
            "diseased_scans": 0,
            "total_crops": 15,
            "most_common_disease": "N/A",
        }

    render_stat_cards(stats)

    col1, col2 = st.columns([3, 2])
    with col1:
        render_features()
    with col2:
        st.markdown(
            f"<h2 style='margin:2rem 0 1.5rem;font-weight:700;font-size:1.1rem;'>{t('home.quick_actions')}</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="card" style="padding:1.5rem;">
        """,
            unsafe_allow_html=True,
        )
        if st.button(
            "🔬 " + t("home.btn_new_detection"), width="stretch", type="primary"
        ):
            st.switch_page("pages/2_Detection.py")
        if st.button("📊 " + t("home.btn_view_analytics"), width="stretch"):
            st.switch_page("pages/3_Analytics.py")
        if st.button("📖 " + t("home.btn_browse_kb"), width="stretch"):
            st.switch_page("pages/4_Knowledge_Base.py")
        if st.button("🌤️ " + t("home.btn_check_weather"), width="stretch"):
            st.switch_page("pages/5_Weather.py")
        st.markdown("</div>", unsafe_allow_html=True)

    render_supported_crops()
    render_workflow()

    st.markdown(
        f"<h2 style='margin:2rem 0 1.5rem;font-weight:700;font-size:1.1rem;'>{t('home.monthly_trends')}</h2>",
        unsafe_allow_html=True,
    )
    render_quick_stats_chart()

    st.markdown(
        f"""
        <div style="text-align:center;padding:2rem;margin-top:2rem;
             background:linear-gradient(135deg, rgba(34,197,94,0.12), rgba(59,130,246,0.08));
             border:1px solid var(--bg-glass-border);
             border-radius:var(--radius-xl);backdrop-filter:blur(20px);">
            <h3 style="font-weight:800;margin-bottom:0.5rem;color:var(--text);
                background:linear-gradient(135deg, #22C55E, #3B82F6);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                {t("home.cta_title")}
            </h3>
            <p style="color:var(--text-secondary);">{t("home.cta_desc")}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
