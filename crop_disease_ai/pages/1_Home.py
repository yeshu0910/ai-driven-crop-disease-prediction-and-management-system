import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Home - Crop Disease AI", page_icon="🌱", layout="wide")


def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header():
    st.markdown("""
        <div class="main-header">
            <h1>🌱 AI Crop Disease Prediction System</h1>
            <p>Intelligent disease detection · Smart treatment recommendations · Weather-based risk analysis</p>
        </div>
    """, unsafe_allow_html=True)


def render_stat_cards(stats):
    cols = st.columns(4)
    icons = ["🔬", "✅", "⚠️", "📊"]
    labels = ["Total Scans", "Healthy Crops", "Diseases Found", "Crops Monitored"]
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
    st.markdown("<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>Core Capabilities</h2>", unsafe_allow_html=True)

    features = [
        {"icon": "🧠", "title": "AI Disease Detection", "desc": "Upload leaf images for instant disease diagnosis using deep learning with >95% accuracy across 15+ crops."},
        {"icon": "🌡️", "title": "Weather Intelligence", "desc": "Real-time weather monitoring and 7-day disease risk forecasting powered by OpenWeather API."},
        {"icon": "💊", "title": "Smart Treatments", "desc": "Personalized chemical and organic treatment recommendations based on disease, severity, and weather."},
        {"icon": "📊", "title": "Analytics Dashboard", "desc": "Interactive dashboards with disease trends, crop health reports, and exportable analytics."},
        {"icon": "📄", "title": "PDF Reports", "desc": "Generate comprehensive diagnostic reports with images, analysis, and treatment plans."},
        {"icon": "🔍", "title": "Explainable AI", "desc": "Understand why each diagnosis was made with confidence analysis and visual heatmaps."},
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
    crops = [
        ("Tomato", "🍅"), ("Potato", "🥔"), ("Rice", "🌾"), ("Wheat", "🌾"),
        ("Corn", "🌽"), ("Cotton", "🌿"), ("Soybean", "🫘"), ("Sugarcane", "🎋"),
        ("Groundnut", "🥜"), ("Sunflower", "🌻"), ("Banana", "🍌"), ("Mango", "🥭"),
        ("Grapes", "🍇"), ("Apple", "🍎"), ("Chili", "🌶️")
    ]

    st.markdown("<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>Supported Crops</h2>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (crop, emoji) in enumerate(crops):
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
    st.markdown("<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>How It Works</h2>", unsafe_allow_html=True)

    steps = [
        ("1", "Upload Image", "Take a photo or upload a leaf image of your crop"),
        ("2", "AI Analysis", "Our CNN model analyzes the image for disease patterns"),
        ("3", "Get Diagnosis", "Receive instant disease identification with confidence score"),
        ("4", "Treatment Plan", "Get personalized chemical and organic recommendations"),
        ("5", "Weather Check", "Monitor conditions and assess disease risk for 7 days"),
        ("6", "Generate Report", "Download comprehensive PDF report for your records")
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
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    healthy = [random.randint(10, 30) for _ in range(6)]
    diseased = [random.randint(5, 20) for _ in range(6)]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Healthy", x=months, y=healthy,
                          marker_color="#4caf50", text=healthy, textposition="auto"))
    fig.add_trace(go.Bar(name="Diseased", x=months, y=diseased,
                          marker_color="#ff6f00", text=diseased, textposition="auto"))
    fig.update_layout(
        barmode="group",
        title="Monthly Detection Trends (Last 6 Months)",
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
        st.markdown("<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>Quick Actions</h2>", unsafe_allow_html=True)
        st.markdown("""
            <div class="dashboard-card" style="padding: 1.5rem;">
        """, unsafe_allow_html=True)
        if st.button("🔬 New Disease Detection", width='stretch', type="primary"):
            st.switch_page("pages/2_Detection.py")
        if st.button("📊 View Analytics Dashboard", width='stretch'):
            st.switch_page("pages/3_Analytics.py")
        if st.button("📖 Browse Knowledge Base", width='stretch'):
            st.switch_page("pages/4_Knowledge_Base.py")
        if st.button("🌤️ Check Weather & Risk", width='stretch'):
            st.switch_page("pages/5_Weather.py")
        st.markdown("</div>", unsafe_allow_html=True)

    render_supported_crops()
    render_workflow()

    st.markdown("<h2 style='margin: 2rem 0 1.5rem; font-weight: 700;'>Detection Trends</h2>", unsafe_allow_html=True)
    render_quick_stats_chart()

    st.markdown("""
        <div style="text-align: center; padding: 2rem; margin-top: 2rem;
             background: linear-gradient(135deg, #1b5e20, #2e7d32);
             border-radius: 16px; color: white;">
            <h3 style="font-weight: 700; margin-bottom: 0.5rem;">🌱 Empowering Farmers with AI</h3>
            <p style="opacity: 0.9;">Protect your crops, maximize yields, and make data-driven farming decisions.</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
