import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(page_title="About - Crop Disease AI", page_icon="ℹ️", layout="wide")


def load_css():
    with open("assets/style.css") as f:
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
            <div class="dashboard-card" style="padding: 2rem;">
                <h2 style="color: #2e7d32; margin-bottom: 1rem;">🌱 Overview</h2>
                <p style="line-height: 1.7; font-size: 1.05rem;">
                    The <strong>AI-Driven Crop Disease Prediction and Management System</strong> is a
                    modern AgriTech web application that leverages artificial intelligence to help
                    farmers detect crop diseases early, receive treatment recommendations, monitor
                    weather conditions, and make data-driven farming decisions.
                </p>
                <p style="line-height: 1.7; margin-top: 1rem;">
                    Built with <strong>Streamlit</strong>, <strong>TensorFlow</strong>,
                    and <strong>Computer Vision</strong>, the system can identify diseases across
                    15+ crops with high accuracy, analyze disease severity, predict future disease
                    risks based on weather conditions, and generate comprehensive PDF reports.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="dashboard-card" style="padding: 2rem; margin-top: 1.5rem;">
                <h2 style="color: #2e7d32; margin-bottom: 1rem;">🚀 Key Features</h2>
        """, unsafe_allow_html=True)

        features = [
            ("🧠", "AI Disease Detection", "CNN-based disease classification with confidence scoring across 15+ crops"),
            ("🌡️", "Weather Intelligence", "Real-time weather monitoring and 7-day disease risk prediction"),
            ("💊", "Smart Treatment Engine", "Personalized chemical and organic treatment recommendations"),
            ("📊", "Farmer Analytics", "Interactive dashboards with disease trends and crop health reports"),
            ("📄", "PDF Report Generation", "Comprehensive diagnostic reports with images and analysis"),
            ("🔍", "Explainable AI", "Transparent predictions with confidence analysis and visual explanations"),
            ("🗄️", "Database System", "SQLite-based record keeping for predictions, weather, and analytics"),
            ("📖", "Knowledge Base", "Comprehensive disease information with search and filter capabilities")
        ]

        for icon, title, desc in features:
            st.markdown(f"""
                <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div>
                        <h4 style="margin: 0; font-weight: 700;">{title}</h4>
                        <p style="margin: 0.2rem 0 0; color: #555;">{desc}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="dashboard-card" style="padding: 2rem;">
                <h3 style="color: #2e7d32; margin-bottom: 1rem;">📋 Tech Stack</h3>
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
            ("🐳", "Docker", "Containerization & deployment")
        ]

        for icon, tech, desc in techs:
            st.markdown(f"""
                <div style="margin: 0.5rem 0;">
                    <strong>{icon} {tech}</strong>
                    <div style="font-size: 0.85rem; color: #666;">{desc}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
            <div class="dashboard-card" style="padding: 2rem; margin-top: 1.5rem;">
                <h3 style="color: #2e7d32; margin-bottom: 1rem;">🌾 Supported Crops</h3>
        """, unsafe_allow_html=True)

        crops = ["Tomato", "Potato", "Rice", "Wheat", "Corn", "Cotton", "Soybean",
                 "Sugarcane", "Groundnut", "Sunflower", "Banana", "Mango", "Grapes", "Apple", "Chili"]
        for crop in crops:
            st.markdown(f"- {crop}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: #2e7d32; font-weight: 700;">🤝 How to Use</h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="dashboard-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2.5rem;">1️⃣</div>
                <h4>Upload or Capture</h4>
                <p style="color: #666; font-size: 0.9rem;">
                    Take a photo or upload a leaf image of your crop
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="dashboard-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2.5rem;">2️⃣</div>
                <h4>Get AI Diagnosis</h4>
                <p style="color: #666; font-size: 0.9rem;">
                    Receive instant disease identification with severity analysis
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="dashboard-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2.5rem;">3️⃣</div>
                <h4>Take Action</h4>
                <p style="color: #666; font-size: 0.9rem;">
                    Follow treatment recommendations and monitor disease risk
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; padding: 3rem; margin-top: 2rem;
             background: linear-gradient(135deg, #1b5e20, #2e7d32);
             border-radius: 16px; color: white;">
            <h3 style="font-weight: 700; margin-bottom: 0.5rem;">🌱 Empowering Farmers with AI Technology</h3>
            <p style="opacity: 0.9; max-width: 600px; margin: 0 auto;">
                Making advanced crop disease detection accessible to everyone,
                helping protect food security and improve farming outcomes.
            </p>
            <p style="margin-top: 1rem; opacity: 0.7; font-size: 0.9rem;">
                Version 1.0.0 | Built with ❤️ for the global farming community
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
