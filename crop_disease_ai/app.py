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
    css_path = Path(__file__).resolve().parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_ambient_background():
    st.markdown("""
        <div class="ambient-blob ambient-blob-1"></div>
        <div class="ambient-blob ambient-blob-2"></div>
        <div class="ambient-blob ambient-blob-3"></div>
    """, unsafe_allow_html=True)


def init_session_state():
    keys = {
        "weather_location": "",
        "farmer_name": "",
        "farm_location": "",
        "db_initialized": False,
        "last_result": None,
        "current_page": "",
    }
    for k, v in keys.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if not st.session_state["db_initialized"]:
        try:
            from database.db_manager import DatabaseManager
            DatabaseManager()
            st.session_state["db_initialized"] = True
        except Exception as e:
            st.error(f"Database initialization failed: {e}")


def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-header">
                <h3>🌱 Crop Disease AI</h3>
                <p>Smart Agriculture Platform</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<p style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.5rem;">Navigation</p>', unsafe_allow_html=True)

        pages = [
            ("🏠", "Home", "1_Home.py"),
            ("🔬", "Disease Detection", "2_Detection.py"),
            ("📊", "Analytics", "3_Analytics.py"),
            ("📖", "Knowledge Base", "4_Knowledge_Base.py"),
            ("🌤️", "Weather", "5_Weather.py"),
            ("📋", "History", "6_History.py"),
            ("ℹ️", "About", "7_About.py"),
        ]

        current = st.session_state.get("current_page", "")
        for icon, label, page_file in pages:
            is_active = current == page_file
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{icon} {label}", key=f"nav_{page_file}",
                         type=btn_type, width='stretch'):
                st.session_state["current_page"] = page_file
                st.switch_page(f"pages/{page_file}")

        st.markdown('<hr style="border-color:var(--border);margin:1rem 0;">', unsafe_allow_html=True)
        with st.expander("👤 Farmer Profile", expanded=False):
            st.session_state["farmer_name"] = st.text_input(
                "Name", value=st.session_state.get("farmer_name", ""),
                placeholder="Enter your name"
            )
            st.session_state["farm_location"] = st.text_input(
                "Location", value=st.session_state.get("farm_location", ""),
                placeholder="Farm location"
            )

        with st.expander("⚙️ Settings", expanded=False):
            st.markdown("""
                <div style="font-size:0.8rem;color:var(--text-muted);text-align:center;margin-top:0.5rem;">
                    Version 1.0.0
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
            <div class="card" style="padding:1.5rem;">
                <h2 class="gradient-text" style="margin-bottom:0.75rem;font-size:1.25rem;">Welcome to the Future of Farming</h2>
                <p style="line-height:1.7;font-size:0.95rem;color:var(--text-secondary);">
                    Leverage the power of <strong>Artificial Intelligence</strong> and
                    <strong>Computer Vision</strong> to protect your crops and maximize yields.
                    Our system can detect diseases from leaf images, analyze severity, provide
                    treatment recommendations, and predict future disease risks based on weather conditions.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 class='section-title'>Quick Actions</h3>", unsafe_allow_html=True)
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        quick_actions = [
            ("🔬", "Detect Disease", "Analyze crop leaf images for disease detection", "pages/2_Detection.py"),
            ("📊", "View Analytics", "Track disease trends and crop health metrics", "pages/3_Analytics.py"),
            ("🌤️", "Weather Risk", "Check weather-based disease risk predictions", "pages/5_Weather.py"),
            ("📖", "Knowledge Base", "Browse comprehensive disease information", "pages/4_Knowledge_Base.py"),
            ("📋", "History", "View past detection records and reports", "pages/6_History.py"),
            ("ℹ️", "About", "Learn about the system and how to use it", "pages/7_About.py"),
        ]
        for icon, label, desc, page in quick_actions:
            st.markdown(f"""
                <div class="feature-card glow-card" style="margin-bottom:0;cursor:pointer;">
                    <div style="font-size:1.8rem;margin-bottom:0.5rem;">{icon}</div>
                    <h4 style="font-weight:700;font-size:0.9rem;margin-bottom:0.25rem;color:var(--text);">{label}</h4>
                    <p style="font-size:0.8rem;color:var(--text-muted);margin:0;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        stats = get_dashboard_stats()
        st.markdown("""
            <div class="card" style="padding:1.25rem;">
                <h3 style="margin-bottom:0.75rem;font-size:0.95rem;color:var(--text);">📊 Quick Stats</h3>
        """, unsafe_allow_html=True)
        stat_items = [
            ("🔬", "Total Scans", stats["total_scans"], "var(--primary)"),
            ("✅", "Healthy", stats["healthy_scans"], "var(--tertiary)"),
            ("⚠️", "Diseased", stats["diseased_scans"], "var(--accent-pink)"),
            ("🌾", "Crops", stats["total_crops"], "#818CF8"),
        ]
        for icon, label, value, color in stat_items:
            st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                     padding:0.5rem 0;border-bottom:1px solid var(--border);font-size:0.85rem;">
                    <span style="color:var(--text-secondary);">{icon} {label}</span>
                    <span style="font-weight:700;color:{color};">{value}</span>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
            <div class="card" style="padding:1.25rem;margin-top:1rem;">
                <h3 style="margin-bottom:0.25rem;font-size:0.95rem;color:var(--text);">💡 Quick Tip</h3>
                <p style="color:var(--text-secondary);font-size:0.85rem;">
                    Upload a clear, well-lit photo of the affected leaf for the most accurate diagnosis.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="glow-card" style="text-align:center;padding:1.5rem;margin-top:1rem;">
            <h3 style="font-weight:700;margin-bottom:0.25rem;color:var(--text);">🌱 Ready to protect your crops?</h3>
            <p style="color:var(--text-secondary);font-size:0.9rem;">
                Navigate to <strong>Disease Detection</strong> to begin analyzing your crops.
            </p>
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
    render_ambient_background()
    init_session_state()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
