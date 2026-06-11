import streamlit as st
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
            <h1>ℹ️ About the System</h1>
            <p>AI-Driven Crop Disease Prediction and Management System</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    load_css()
    render_header()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
            <div class="card" style="padding:1.5rem;">
                <h2 class="gradient-text" style="margin-bottom:0.75rem;">🌱 Overview</h2>
                <p style="line-height:1.7;font-size:0.95rem;color:var(--text-secondary);">
                    The <strong>AI-Driven Crop Disease Prediction and Management System</strong> is a
                    modern AgriTech web application that leverages artificial intelligence to help
                    farmers detect crop diseases early, receive treatment recommendations, monitor
                    weather conditions, and make data-driven farming decisions.
                </p>
                <p style="line-height:1.7;margin-top:0.75rem;font-size:0.95rem;color:var(--text-secondary);">
                    Built with <strong>Streamlit</strong>, <strong>TensorFlow</strong>,
                    and <strong>Computer Vision</strong>, the system can identify diseases across
                    15+ crops, analyze disease severity, predict future disease risks based on
                    weather conditions, and generate comprehensive PDF reports.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="card" style="padding:1.5rem;margin-top:1rem;">
                <h2 class="gradient-text" style="margin-bottom:0.75rem;">🚀 Key Features</h2>
        """, unsafe_allow_html=True)

        features = [
            ("🧠", "AI Disease Detection", "CNN-based disease classification with confidence scoring across 15+ crops"),
            ("🌡️", "Weather Intelligence", "Real-time weather monitoring and 7-day disease risk prediction"),
            ("💊", "Smart Treatment Engine", "Personalized chemical and organic treatment recommendations"),
            ("📊", "Farmer Analytics", "Interactive dashboards with disease trends and crop health reports"),
            ("📄", "PDF Report Generation", "Comprehensive diagnostic reports with images and analysis"),
            ("🔍", "Explainable AI", "Transparent predictions with confidence analysis and visual explanations"),
            ("🗄️", "Database System", "SQLite-based record keeping for predictions, weather, and analytics"),
            ("📖", "Knowledge Base", "Comprehensive disease information with search and filter capabilities"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
                <div style="display:flex;gap:0.75rem;margin:0.75rem 0;">
                    <div style="font-size:1.5rem;flex-shrink:0;">{icon}</div>
                    <div>
                        <h4 style="margin:0;font-weight:700;font-size:0.9rem;">{title}</h4>
                        <p style="margin:0.15rem 0 0;color:var(--text-secondary);font-size:0.85rem;">{desc}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="card" style="padding:1.25rem;">
                <h3 class="gradient-text-primary" style="margin-bottom:0.75rem;font-size:1rem;">📋 Tech Stack</h3>
        """, unsafe_allow_html=True)
        techs = [
            ("🐍", "Python 3.11+", "Core programming language"),
            ("🌐", "Streamlit", "Web application framework"),
            ("🧠", "TensorFlow/Keras", "Deep learning framework"),
            ("👁️", "OpenCV", "Computer vision & image processing"),
            ("📊", "Plotly", "Interactive data visualization"),
            ("🗄️", "SQLite", "Relational database system"),
            ("🌤️", "OpenWeather API", "Weather data integration"),
            ("📄", "ReportLab", "PDF generation engine"),
            ("📈", "Scikit-learn", "ML utilities & evaluation"),
            ("🐳", "Docker", "Containerization & deployment"),
        ]
        for icon, tech, desc in techs:
            st.markdown(f"""
                <div style="margin:0.4rem 0;font-size:0.85rem;">
                    <strong>{icon} {tech}</strong>
                    <div style="font-size:0.75rem;color:var(--text-muted);">{desc}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
            <div class="card" style="padding:1.25rem;margin-top:1rem;">
                <h3 class="gradient-text-primary" style="margin-bottom:0.5rem;font-size:1rem;">🌾 Supported Crops</h3>
        """, unsafe_allow_html=True)
        crops = ["Tomato", "Potato", "Rice", "Wheat", "Corn", "Cotton", "Soybean",
                 "Sugarcane", "Groundnut", "Sunflower", "Banana", "Mango", "Grapes", "Apple", "Chili"]
        for crop in crops:
            st.markdown(f"<div style='font-size:0.85rem;padding:0.1rem 0;'>{crop}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div style="text-align:center;padding:1.5rem 0;">
            <h2 class="gradient-text" style="font-weight:700;font-size:1.3rem;">🤝 How to Use</h2>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
            <div class="card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:2rem;">1️⃣</div>
                <h4 style="font-size:0.95rem;">Upload or Capture</h4>
                <p style="color:var(--text-secondary);font-size:0.85rem;">Take a photo or upload a leaf image of your crop</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class="card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:2rem;">2️⃣</div>
                <h4 style="font-size:0.95rem;">Get AI Diagnosis</h4>
                <p style="color:var(--text-secondary);font-size:0.85rem;">Receive instant disease identification with severity analysis</p>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class="card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:2rem;">3️⃣</div>
                <h4 style="font-size:0.95rem;">Take Action</h4>
                <p style="color:var(--text-secondary);font-size:0.85rem;">Follow treatment recommendations and monitor disease risk</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="glow-card" style="text-align:center;padding:2rem;margin-top:1.5rem;">
            <h3 style="font-weight:700;margin-bottom:0.25rem;color:var(--text);">🌱 Empowering Farmers with AI Technology</h3>
            <p style="color:var(--text-secondary);font-size:0.9rem;max-width:600px;margin:0 auto;">
                Making advanced crop disease detection accessible to everyone,
                helping protect food security and improve farming outcomes.
            </p>
            <p style="margin-top:0.75rem;color:var(--text-muted);font-size:0.8rem;">
                Version 1.0.0 | Built with ❤️ for the global farming community
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
