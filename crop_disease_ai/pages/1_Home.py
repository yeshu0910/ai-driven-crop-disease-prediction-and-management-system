import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.translator import t

st.set_page_config(page_title=t("app.title") + " - " + t("nav.home"), page_icon="🌱", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets/style.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)




def render_header():
    st.markdown(f"""
        <div class="main-header">
            <h1>{t("home.title")}</h1>
            <p>{t("home.subtitle")}</p>
        </div>
    """, unsafe_allow_html=True)


def render_stat_cards(stats):
    cols = st.columns(4)
    icons = ["🔬", "✅", "⚠️", "📊"]
    labels = [t("stats.total_scans"), t("stats.healthy_crops"), t("stats.diseases_found"), t("stats.crops_monitored")]
    colors = ["#2e7d32", "#4caf50", "#ff6f00", "#1976d2"]

    for i, (col, icon, label, color) in enumerate(zip(cols, icons, labels, colors)):
        value = list(stats.values())[i] if i < len(stats) else 0
        col.markdown(f"""
            <div class="dashboard-card animate-in" style="animation-delay: {i*0.1}s">
                <div class="card-icon" style="background: {color}15; color: {color}">{icon}</div>
                <div class="card-label">{label}</div>
                <div class="card-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)


def render_features():
    st.markdown(f"<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>{t('home.core_capabilities')}</h2>", unsafe_allow_html=True)

    features = [
        {"icon": "🧠", "title": t("home.feature_ai_title"), "desc": t("home.feature_ai_desc")},
        {"icon": "🌡️", "title": t("home.feature_weather_title"), "desc": t("home.feature_weather_desc")},
        {"icon": "💊", "title": t("home.feature_treatment_title"), "desc": t("home.feature_treatment_desc")},
        {"icon": "📊", "title": t("home.feature_analytics_title"), "desc": t("home.feature_analytics_desc")},
        {"icon": "📄", "title": t("home.feature_pdf_title"), "desc": t("home.feature_pdf_desc")},
        {"icon": "🔍", "title": t("home.feature_xai_title"), "desc": t("home.feature_xai_desc")},
    ]

    cols = st.columns(3)
    for i, feat in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="dashboard-card" style="margin-bottom: 1.5rem; padding: 1.8rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">{feat['icon']}</div>
                    <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">{feat['title']}</h3>
                    <p style="color: #666; font-size: 0.9rem; line-height: 1.5;">{feat['desc']}</p>
                </div>
            """, unsafe_allow_html=True)


def render_supported_crops():
    crops_list = [
        (t("home.crop_tomato"), "🍅"), (t("home.crop_potato"), "🥔"), (t("home.crop_rice"), "🌾"),
        (t("home.crop_wheat"), "🌾"), (t("home.crop_corn"), "🌽"), (t("home.crop_cotton"), "🌿"),
        (t("home.crop_soybean"), "🫘"), (t("home.crop_sugarcane"), "🎋"), (t("home.crop_groundnut"), "🥜"),
        (t("home.crop_sunflower"), "🌻"), (t("home.crop_banana"), "🍌"), (t("home.crop_mango"), "🥭"),
        (t("home.crop_grapes"), "🍇"), (t("home.crop_apple"), "🍎"), (t("home.crop_chili"), "🌶️")
    ]

    st.markdown(f"<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>{t('home.supported_crops')}</h2>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (crop, emoji) in enumerate(crops_list):
        with cols[i % 5]:
            st.markdown(f"""
                <div style="text-align: center; padding: 0.8rem; margin-bottom: 0.5rem;
                     background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                     transition: all 0.3s;">
                    <div style="font-size: 2rem;">{emoji}</div>
                    <div style="font-weight: 600; font-size: 0.85rem; color: #333;">{crop}</div>
                </div>
            """, unsafe_allow_html=True)


def render_workflow():
    st.markdown(f"<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>{t('home.how_it_works')}</h2>", unsafe_allow_html=True)

    steps = [
        ("1", t("home.step1_title"), t("home.step1_desc")),
        ("2", t("home.step2_title"), t("home.step2_desc")),
        ("3", t("home.step3_title"), t("home.step3_desc")),
        ("4", t("home.step4_title"), t("home.step4_desc")),
        ("5", t("home.step5_title"), t("home.step5_desc")),
        ("6", t("home.step6_title"), t("home.step6_desc"))
    ]

    cols = st.columns(6)
    for i, (num, title, desc) in enumerate(steps):
        with cols[i]:
            st.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <div style="width: 40px; height: 40px; border-radius: 50%;
                         background: linear-gradient(135deg, #2e7d32, #1b5e20);
                         color: white; display: flex; align-items: center;
                         justify-content: center; margin: 0 auto 0.8rem;
                         font-weight: 700; font-size: 1.1rem;">{num}</div>
                    <h4 style="font-size: 0.85rem; font-weight: 700; margin-bottom: 0.3rem;">{title}</h4>
                    <p style="font-size: 0.75rem; color: #888; line-height: 1.4;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)
            if i < 5:
                st.markdown("""
                    <div style="text-align: center; color: #2e7d32; font-weight: 700;
                         font-size: 1.2rem; margin-top: -2rem;">→</div>
                """, unsafe_allow_html=True)


def render_quick_stats_chart():
    months = [t("month.jan"), t("month.feb"), t("month.mar"), t("month.apr"), t("month.may"), t("month.jun")]
    healthy = [random.randint(10, 30) for _ in range(6)]
    diseased = [random.randint(5, 20) for _ in range(6)]

    fig = go.Figure()
    fig.add_trace(go.Bar(name=t("home.chart_healthy"), x=months, y=healthy,
                          marker_color="#4caf50", text=healthy, textposition="auto"))
    fig.add_trace(go.Bar(name=t("home.chart_diseased"), x=months, y=diseased,
                          marker_color="#ff6f00", text=diseased, textposition="auto"))
    fig.update_layout(
        barmode="group",
        title=t("home.monthly_trends"),
        template="plotly_white",
        hovermode="x",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, width='stretch')


def main():
    load_css()
    render_header()

    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    stats = db.get_summary_stats()

    if stats["total_scans"] == 0:
        stats = {"total_scans": 0, "healthy_scans": 0, "diseased_scans": 0,
                 "total_crops": 15, "most_common_disease": "N/A"}

    render_stat_cards(stats)

    col1, col2 = st.columns([3, 2])
    with col1:
        render_features()
    with col2:
        st.markdown(f"<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>{t('home.quick_actions')}</h2>", unsafe_allow_html=True)
        st.markdown("""
            <div class="dashboard-card" style="padding: 1.5rem;">
        """, unsafe_allow_html=True)
        if st.button(t("home.btn_new_detection"), width='stretch', type="primary"):
            st.switch_page("pages/2_Detection.py")
        if st.button(t("home.btn_view_analytics"), width='stretch'):
            st.switch_page("pages/3_Analytics.py")
        if st.button(t("home.btn_browse_kb"), width='stretch'):
            st.switch_page("pages/4_Knowledge_Base.py")
        if st.button(t("home.btn_check_weather"), width='stretch'):
            st.switch_page("pages/5_Weather.py")
        st.markdown("</div>", unsafe_allow_html=True)

    render_supported_crops()
    render_workflow()

    st.markdown(f"<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>{t('home.monthly_trends')}</h2>", unsafe_allow_html=True)
    render_quick_stats_chart()

    st.markdown(f"""
        <div style="text-align: center; padding: 2rem; margin-top: 2rem;
             background: linear-gradient(135deg, #1b5e20, #2e7d32);
             border-radius: 16px; color: white;">
            <h3 style="font-weight: 700; margin-bottom: 0.5rem;">{t("home.footer_text")}</h3>
            <p style="opacity: 0.9;">{t("home.footer_subtext")}</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
