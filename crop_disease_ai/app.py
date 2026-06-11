import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

st.set_page_config(
    page_title="Crop Disease AI - Smart Agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_session_state():
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    if "weather_location" not in st.session_state:
        st.session_state["weather_location"] = ""
    if "farmer_name" not in st.session_state:
        st.session_state["farmer_name"] = ""
    if "farm_location" not in st.session_state:
        st.session_state["farm_location"] = ""
    if "db_initialized" not in st.session_state:
        from database.db_manager import DatabaseManager
        DatabaseManager()
        st.session_state["db_initialized"] = True


def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-header">
                <h3>🌱 Crop Disease AI</h3>
                <p style="font-size: 0.8rem; opacity: 0.8;">Smart Agriculture Platform</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### Navigation")
        pages = {
            "🏠 Home": "1_Home.py",
            "🔬 Disease Detection": "2_Detection.py",
            "📊 Analytics": "3_Analytics.py",
            "📖 Knowledge Base": "4_Knowledge_Base.py",
            "🌤️ Weather": "5_Weather.py",
            "📋 History": "6_History.py",
            "ℹ️ About": "7_About.py"
        }

        for label, page_file in pages.items():
            if st.button(label, width='stretch',
                         type="secondary" if st.session_state.get("current_page") != page_file else "primary"):
                st.session_state["current_page"] = page_file
                st.switch_page(f"pages/{page_file}")

        st.markdown("---")
        st.markdown("### 👤 Farmer Profile")
        st.session_state["farmer_name"] = st.text_input(
            "Name", value=st.session_state.get("farmer_name", ""),
            placeholder="Enter your name"
        )
        st.session_state["farm_location"] = st.text_input(
            "Location", value=st.session_state.get("farm_location", ""),
            placeholder="Farm location"
        )

        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        theme = st.selectbox(
            "Theme",
            ["Light", "Dark"],
            index=0 if st.session_state.get("theme") == "light" else 1
        )
        st.session_state["theme"] = theme.lower()

        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0; font-size: 0.8rem; color: #888;">
                <p>🌱 AI Crop Disease AI</p>
                <p>Version 1.0.0</p>
            </div>
        """, unsafe_allow_html=True)


def render_main():
    st.markdown("""
        <div class="main-header">
            <h1>🌱 AI-Driven Crop Disease Prediction System</h1>
            <p>Intelligent disease detection · Smart recommendations · Weather-based risk analysis</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
            <div class="dashboard-card" style="padding: 2rem;">
                <h2 style="color: #2e7d32; margin-bottom: 1rem;">Welcome to the Future of Farming</h2>
                <p style="line-height: 1.7; font-size: 1.05rem;">
                    Leverage the power of <strong>Artificial Intelligence</strong> and
                    <strong>Computer Vision</strong> to protect your crops and maximize yields.
                    Our system can detect diseases from leaf images, analyze severity, provide
                    treatment recommendations, and predict future disease risks based on weather conditions.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
        """, unsafe_allow_html=True)

        quick_actions = [
            ("🔬", "Detect Disease", "Analyze crop leaf images for disease detection", "pages/2_Detection.py"),
            ("📊", "View Analytics", "Track disease trends and crop health metrics", "pages/3_Analytics.py"),
            ("🌤️", "Weather Risk", "Check weather-based disease risk predictions", "pages/5_Weather.py"),
            ("📖", "Knowledge Base", "Browse comprehensive disease information", "pages/4_Knowledge_Base.py"),
            ("📋", "History", "View past detection records and reports", "pages/6_History.py"),
            ("ℹ️", "About", "Learn about the system and how to use it", "pages/7_About.py")
        ]

        for icon, label, desc, page in quick_actions:
            st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 1.2rem;
                     box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;
                     transition: all 0.3s; cursor: pointer;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <h4 style="margin: 0.5rem 0 0.2rem; font-weight: 700;">{label}</h4>
                    <p style="font-size: 0.8rem; color: #888; margin: 0;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        stats = get_dashboard_stats()
        st.markdown("""
            <div class="dashboard-card" style="padding: 1.5rem;">
                <h3 style="margin-bottom: 1rem;">📊 Quick Stats</h3>
        """, unsafe_allow_html=True)

        stat_items = [
            ("🔬", "Total Scans", stats["total_scans"], "#2e7d32"),
            ("✅", "Healthy", stats["healthy_scans"], "#4caf50"),
            ("⚠️", "Diseased", stats["diseased_scans"], "#ff6f00"),
            ("🌾", "Crops", stats["total_crops"], "#1976d2")
        ]
        for icon, label, value, color in stat_items:
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center;
                     padding: 0.6rem 0; border-bottom: 1px solid #f0f0f0;">
                    <span>{icon} {label}</span>
                    <span style="font-weight: 700; color: {color};">{value}</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
            <div class="dashboard-card" style="padding: 1.5rem; margin-top: 1rem;">
                <h3 style="margin-bottom: 0.5rem;">💡 Quick Tip</h3>
                <p style="color: #555; font-size: 0.9rem;">
                    Upload a clear, well-lit photo of the affected leaf for the most accurate diagnosis.
                    Capture from multiple angles if possible.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 1.5rem; margin-top: 1rem;
             background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
             border-radius: 16px;">
            <h3 style="color: #2e7d32; font-weight: 700;">🌱 Ready to protect your crops?</h3>
            <p style="color: #555;">Navigate to <strong>Disease Detection</strong> to begin analyzing your crops.</p>
        </div>
    """, unsafe_allow_html=True)


def get_dashboard_stats():
    try:
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        stats = db.get_summary_stats()
        if stats["total_scans"] == 0:
            return {"total_scans": 0, "healthy_scans": 0, "diseased_scans": 0,
                    "total_crops": 15, "most_common_disease": "N/A"}
        return stats
    except Exception:
        return {"total_scans": 0, "healthy_scans": 0, "diseased_scans": 0,
                "total_crops": 15, "most_common_disease": "N/A"}


def main():
    load_css()
    init_session_state()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
