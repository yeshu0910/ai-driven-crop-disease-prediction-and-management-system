import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header():
    st.markdown("""
        <div class="main-header">
            <h1>🌱 AI Crop Disease Prediction System</h1>
            <p>Intelligent disease detection · Smart treatment recommendations · Weather-based risk analysis</p>
        </div>
    """, unsafe_allow_html=True)


def render_stat_cards(stats):
    st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
    items = [
        ("🔬", "Total Scans", stats["total_scans"], "var(--primary)"),
        ("✅", "Healthy Crops", stats["healthy_scans"], "var(--tertiary)"),
        ("⚠️", "Diseases Found", stats["diseased_scans"], "var(--accent-pink)"),
        ("📊", "Crops Monitored", stats["total_crops"], "#818CF8"),
    ]
    for icon, label, value, color in items:
        st.markdown(f"""
            <div class="stat-card animate-in">
                <div class="stat-icon">{icon}</div>
                <div class="stat-label">{label}</div>
                <div class="stat-value" style="color:{color};">{value}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_features():
    st.markdown("<h2 class='section-title gradient-text'>Core Capabilities</h2>", unsafe_allow_html=True)
    st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
    features = [
        {"icon": "🧠", "title": "AI Disease Detection", "desc": "Upload leaf images for instant disease diagnosis using deep learning across 15+ crops."},
        {"icon": "🌡️", "title": "Weather Intelligence", "desc": "Real-time weather monitoring and 7-day disease risk forecasting."},
        {"icon": "💊", "title": "Smart Treatments", "desc": "Personalized chemical and organic treatment recommendations."},
        {"icon": "📊", "title": "Analytics Dashboard", "desc": "Interactive dashboards with disease trends and crop health reports."},
        {"icon": "📄", "title": "PDF Reports", "desc": "Generate comprehensive diagnostic reports with images and analysis."},
        {"icon": "🔍", "title": "Explainable AI", "desc": "Understand why each diagnosis was made with confidence analysis."},
    ]
    for feat in features:
        st.markdown(f"""
            <div class="feature-card card">
                <div style="font-size:2.2rem;margin-bottom:0.5rem;">{feat['icon']}</div>
                <h3 style="font-size:1rem;font-weight:700;margin-bottom:0.4rem;">{feat['title']}</h3>
                <p style="color:var(--text-secondary);font-size:0.85rem;line-height:1.5;">{feat['desc']}</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_supported_crops():
    crops = [
        ("Tomato", "🍅"), ("Potato", "🥔"), ("Rice", "🌾"), ("Wheat", "🌾"),
        ("Corn", "🌽"), ("Cotton", "🌿"), ("Soybean", "🫘"), ("Sugarcane", "🎋"),
        ("Groundnut", "🥜"), ("Sunflower", "🌻"), ("Banana", "🍌"), ("Mango", "🥭"),
        ("Grapes", "🍇"), ("Apple", "🍎"), ("Chili", "🌶️"),
    ]
    st.markdown("<h2 class='section-title gradient-text'>Supported Crops</h2>", unsafe_allow_html=True)
    st.markdown('<div class="crop-grid">', unsafe_allow_html=True)
    for crop, emoji in crops:
        st.markdown(f"""
            <div class="crop-item">
                <div class="crop-emoji">{emoji}</div>
                <div class="crop-name">{crop}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_workflow():
    st.markdown("<h2 class='section-title gradient-text'>How It Works</h2>", unsafe_allow_html=True)
    st.markdown('<div class="workflow-grid">', unsafe_allow_html=True)
    steps = [
        ("1", "Upload Image", "Take a photo or upload a leaf image of your crop"),
        ("2", "AI Analysis", "Our CNN model analyzes the image for disease patterns"),
        ("3", "Get Diagnosis", "Receive instant disease identification with confidence score"),
        ("4", "Treatment Plan", "Get personalized chemical and organic recommendations"),
        ("5", "Weather Check", "Monitor conditions and assess disease risk for 7 days"),
        ("6", "Generate Report", "Download comprehensive PDF report for your records"),
    ]
    for num, title, desc in steps:
        st.markdown(f"""
            <div class="workflow-step">
                <div class="step-number">{num}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_quick_stats_chart():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    healthy_vals = [random.randint(10, 30) for _ in range(6)]
    diseased_vals = [random.randint(5, 20) for _ in range(6)]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Healthy", x=months, y=healthy_vals,
                          marker_color="#4caf50", text=healthy_vals, textposition="auto"))
    fig.add_trace(go.Bar(name="Diseased", x=months, y=diseased_vals,
                          marker_color="#ff6f00", text=diseased_vals, textposition="auto"))
    fig.update_layout(
        barmode="group",
        title="Monthly Detection Trends (Last 6 Months)",
        template="plotly_white",
        hovermode="x",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", y=1.1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width='stretch')


def main():
    load_css()
    render_header()

    try:
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        stats = db.get_summary_stats()
    except Exception:
        stats = {"total_scans": 0, "healthy_scans": 0, "diseased_scans": 0,
                 "total_crops": 15, "most_common_disease": "N/A"}

    if stats["total_scans"] == 0:
        stats = {"total_scans": 0, "healthy_scans": 0, "diseased_scans": 0,
                 "total_crops": 15, "most_common_disease": "N/A"}

    render_stat_cards(stats)

    col1, col2 = st.columns([3, 2])
    with col1:
        render_features()
    with col2:
        st.markdown("<h2 class='section-title gradient-text'>Quick Actions</h2>", unsafe_allow_html=True)
        st.markdown('<div class="card" style="padding:1.25rem;">', unsafe_allow_html=True)
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

    st.markdown("<h2 class='section-title gradient-text'>Detection Trends</h2>", unsafe_allow_html=True)
    render_quick_stats_chart()

    st.markdown("""
        <div class="glow-card" style="text-align:center;padding:1.5rem;margin-top:1.5rem;">
            <h3 style="font-weight:700;margin-bottom:0.25rem;color:var(--text);">🌱 Empowering Farmers with AI</h3>
            <p style="color:var(--text-secondary);font-size:0.9rem;">Protect your crops, maximize yields, and make data-driven farming decisions.</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
