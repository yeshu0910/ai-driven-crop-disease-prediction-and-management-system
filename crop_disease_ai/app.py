import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.translator import t, load_translations, get_supported_languages

st.set_page_config(
    page_title=t("app.title"),
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
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    if "weather_location" not in st.session_state:
        st.session_state["weather_location"] = ""
    if "farmer_name" not in st.session_state:
        st.session_state["farmer_name"] = ""
    if "farm_location" not in st.session_state:
        st.session_state["farm_location"] = ""
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    if "db_initialized" not in st.session_state:
        from database.db_manager import DatabaseManager
        DatabaseManager()
        st.session_state["db_initialized"] = True
    if "language" not in st.session_state:
        st.session_state["language"] = "en"


def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-header">
                <h3>{t("sidebar.header_title")}</h3>
                <p style="font-size: 0.8rem; opacity: 0.8;">{t("sidebar.header_subtitle")}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### {t('nav.navigation')}")
        pages = {
            t("nav.home"): "1_Home.py",
            t("nav.detection"): "2_Detection.py",
            t("nav.analytics"): "3_Analytics.py",
            t("nav.knowledge_base"): "4_Knowledge_Base.py",
            t("nav.weather"): "5_Weather.py",
            t("nav.history"): "6_History.py",
            t("nav.about"): "7_About.py"
        }

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

        st.markdown("---")
        st.markdown(f"### {t('sidebar.farmer_profile')}")
        st.session_state["farmer_name"] = st.text_input(
            t("sidebar.name"), value=st.session_state.get("farmer_name", ""),
            placeholder=t("sidebar.name_placeholder")
        )
        st.session_state["farm_location"] = st.text_input(
            t("sidebar.location"), value=st.session_state.get("farm_location", ""),
            placeholder=t("sidebar.location_placeholder")
        )

        st.markdown("---")
        st.markdown(f"### {t('sidebar.settings')}")
        theme_options = [t("sidebar.light"), t("sidebar.dark")]
        theme = st.selectbox(
            t("sidebar.theme"),
            theme_options,
            index=0 if st.session_state.get("theme") == "light" else 1
        )
        st.session_state["theme"] = "light" if theme == t("sidebar.light") else "dark"

        langs = get_supported_languages()
        lang_labels = {"en": "English", "hi": "हिन्दी", "te": "తెలుగు"}
        lang_options = [f"{lang_labels.get(l, l.upper())}" for l in langs]
        current_lang = st.session_state.get("language", "en")
        lang_idx = langs.index(current_lang) if current_lang in langs else 0
        selected_lang = st.selectbox(
            t("app.language"), lang_options, index=lang_idx
        )
        new_lang = langs[lang_options.index(selected_lang)]
        if new_lang != current_lang:
            st.session_state["language"] = new_lang
            load_translations(new_lang)
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0; font-size: 0.8rem; color: #888;">
                <p>{t("app.footer_title")}</p>
                <p>{t("app.version")}</p>
            </div>
        """, unsafe_allow_html=True)


def render_main():
    st.markdown(f"""
        <div class="main-header">
            <h1>{t("app.main_title")}</h1>
            <p>{t("app.subtitle")}</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
            <div class="dashboard-card" style="padding: 2rem;">
                <h2 style="color: #2e7d32; margin-bottom: 1rem;">{t("welcome.title")}</h2>
                <p style="line-height: 1.7; font-size: 1.05rem;">
                    {t("welcome.description")}
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 class='section-title'>Quick Actions</h3>", unsafe_allow_html=True)
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        quick_actions = [
            ("🔬", t("quick_action.detect"), t("quick_action.detect_desc"), "pages/2_Detection.py"),
            ("📊", t("quick_action.analytics"), t("quick_action.analytics_desc"), "pages/3_Analytics.py"),
            ("🌤️", t("quick_action.weather"), t("quick_action.weather_desc"), "pages/5_Weather.py"),
            ("📖", t("quick_action.knowledge"), t("quick_action.knowledge_desc"), "pages/4_Knowledge_Base.py"),
            ("📋", t("quick_action.history"), t("quick_action.history_desc"), "pages/6_History.py"),
            ("ℹ️", t("quick_action.about"), t("quick_action.about_desc"), "pages/7_About.py")
        ]
        for icon, label, desc, _page in quick_actions:
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
        st.markdown(f"""
            <div class="dashboard-card" style="padding: 1.5rem;">
                <h3 style="margin-bottom: 1rem;">{t("stats.quick_stats")}</h3>
        """, unsafe_allow_html=True)
        stat_items = [
            ("🔬", t("stats.total_scans"), stats["total_scans"], "#2e7d32"),
            ("✅", t("stats.healthy"), stats["healthy_scans"], "#4caf50"),
            ("⚠️", t("stats.diseased"), stats["diseased_scans"], "#ff6f00"),
            ("🌾", t("stats.crops"), stats["total_crops"], "#1976d2")
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

        st.markdown(f"""
            <div class="dashboard-card" style="padding: 1.5rem; margin-top: 1rem;">
                <h3 style="margin-bottom: 0.5rem;">{t("tip.title")}</h3>
                <p style="color: #555; font-size: 0.9rem;">
                    {t("tip.description")}
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; margin-top: 1rem;
             background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
             border-radius: 16px;">
            <h3 style="color: #2e7d32; font-weight: 700;">{t("welcome.cta_title")}</h3>
            <p style="color: #555;">{t("welcome.cta_subtitle")}</p>
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
    init_session_state()
    lang = st.session_state.get("language", "en")
    load_translations(lang)
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
