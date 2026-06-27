import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.translator import get_supported_languages, load_translations, t

st.set_page_config(
    page_title=t("app.title"),
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    css_path = Path(__file__).resolve().parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_ambient_background():
    st.markdown(
        """
        <div class="ambient-blob ambient-blob-1"></div>
        <div class="ambient-blob ambient-blob-2"></div>
        <div class="ambient-blob ambient-blob-3"></div>
    """,
        unsafe_allow_html=True,
    )


# ===== REUSABLE UI HELPERS =====


def render_card(title="", content="", icon="", style_extra=""):
    """Render a glassmorphism card with optional icon, title, and content HTML."""
    icon_html = (
        f'<div style="font-size:1.8rem;margin-bottom:0.75rem;">{icon}</div>'
        if icon
        else ""
    )
    title_html = (
        f'<h3 style="font-size:1rem;font-weight:700;margin-bottom:0.5rem;color:var(--text);">{title}</h3>'
        if title
        else ""
    )
    st.markdown(
        f"""
        <div class="card" style="{style_extra}">
            {icon_html}
            {title_html}
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(
    label, value, icon="", color="var(--primary)", border_color="var(--primary)"
):
    """Render a compact metric card with label, value, and colored left border."""
    icon_html = f'<span style="margin-right:0.5rem;">{icon}</span>' if icon else ""
    st.markdown(
        f"""
        <div class="metric-card" style="border-left-color:{border_color};">
            <div class="metric-label">{icon_html}{label}</div>
            <div class="metric-value" style="color:{color};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title, subtitle=""):
    """Render a section header with optional subtitle."""
    subtitle_html = (
        f'<p style="color:var(--text-secondary);font-size:0.85rem;margin-top:0.25rem;">{subtitle}</p>'
        if subtitle
        else ""
    )
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        {subtitle_html}
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(icon, label, value, color="#22C55E", delay=0):
    """Render a stat card with icon, label, large value, and staggered animation."""
    st.markdown(
        f"""
        <div class="stat-card animate-in animate-delay-{delay}" style="animation-delay:{delay * 0.1}s;">
            <div style="width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;
                 font-size:1.4rem;margin:0 auto 0.75rem;background:{color}15;border:1px solid {color}30;">{icon}</div>
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badge(text, variant="green"):
    """Return HTML for a badge."""
    return f'<span class="badge badge-{variant}">{text}</span>'


def render_hero_section(title, subtitle, badge_text=None):
    """Render a premium hero section with badge, title, and subtitle."""
    badge_html = f'<div class="hero-badge">✨ {badge_text}</div>' if badge_text else ""
    st.markdown(
        f"""
        <div class="hero-section">
            {badge_html}
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title, subtitle=""):
    """Render a standard page header (non-hero)."""
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_session_state():
    """Safely initialise ALL required session_state keys at startup."""
    defaults = {
        "theme": "dark",
        "weather_location": "",
        "farmer_name": "",
        "farm_location": "",
        "language": "en",
        "db_initialized": False,
        "current_page": "",
        "last_result": None,
        "prediction_history": [],
        "detection_settings": {
            "confidence_threshold": 0.5,
            "model_variant": "default",
            "enable_xai": True,
            "enable_severity": True,
            "enable_weather": True,
        },
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state["db_initialized"]:
        try:
            from database.db_manager import DatabaseManager

            DatabaseManager()
            st.session_state["db_initialized"] = True
        except Exception as e:
            st.error(f"Database initialization failed: {e}")


def render_sidebar():
    with st.sidebar:
        # Premium logo
        st.markdown(
            """
            <div class="sidebar-logo">
                <div class="logo-icon">🌱</div>
                <div class="logo-text">CropHealth AI</div>
                <div class="logo-sub">Disease Detection System</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Navigation
        st.markdown(
            '<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True
        )

        pages = [
            ("🏠", "Home", "1_Home.py"),
            ("🔬", "Disease Detection", "2_Detection.py"),
            ("📊", "Analytics", "3_Analytics.py"),
            ("📖", "Knowledge Base", "4_Knowledge_Base.py"),
            ("🌤️", "Weather", "5_Weather.py"),
            ("📋", "History", "6_History.py"),
            ("🤖", "AI Assistant", "8_AI_Assistant.py"),
            ("ℹ️", "About", "7_About.py"),
        ]

        current = st.session_state.get("current_page", "")
        for icon, label, page_file in pages:
            is_active = current == page_file
            btn_type = "primary" if is_active else "secondary"

            if st.button(
                f"{icon} {label}",
                key=f"nav_{page_file}",
                type=btn_type,
                use_container_width=True,
            ):
                st.session_state["current_page"] = page_file
                st.switch_page(f"pages/{page_file}")

        # Farmer Profile Section
        st.markdown("---")
        st.markdown(
            '<div class="sidebar-section">Farmer Profile</div>', unsafe_allow_html=True
        )

        st.session_state["farmer_name"] = st.text_input(
            "👤 " + t("sidebar.name"),
            value=st.session_state.get("farmer_name", ""),
            placeholder=t("sidebar.name_placeholder"),
            label_visibility="collapsed",
        )

        st.session_state["farm_location"] = st.text_input(
            "📍 " + t("sidebar.location"),
            value=st.session_state.get("farm_location", ""),
            placeholder=t("sidebar.location_placeholder"),
            label_visibility="collapsed",
        )

        # Settings Section
        st.markdown("---")
        st.markdown(
            '<div class="sidebar-section">Settings</div>', unsafe_allow_html=True
        )

        langs = get_supported_languages()
        lang_labels = {"en": "English", "hi": "हिन्दी", "te": "తెలుగు"}
        lang_options = [lang_labels.get(lang, lang.upper()) for lang in langs]

        current_lang = st.session_state.get("language", "en")
        lang_idx = langs.index(current_lang) if current_lang in langs else 0

        selected_lang = st.selectbox("🌐 Language", lang_options, index=lang_idx)

        new_lang = langs[lang_options.index(selected_lang)]

        if new_lang != current_lang:
            st.session_state["language"] = new_lang
            load_translations(new_lang)
            st.rerun()

        # Footer
        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align:center;padding:1rem 0;font-size:0.7rem;color:var(--text-muted);">
                <p>{t("app.footer_title")}</p>
                <p>{t("app.version")}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )


def render_main():
    """Home page with hero section."""
    render_hero_section(
        title="AI-Powered <em>Crop Disease</em> Detection",
        subtitle="Upload a leaf image and get instant AI-powered diagnosis, treatment recommendations, and weather-based risk analysis — all in seconds.",
        badge_text="Powered by Deep Learning",
    )

    # CTA buttons below hero
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        if st.button(
            "🔬 Detect Disease",
            key="hero_detect",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page("pages/2_Detection.py")
    with col_btn2:
        if st.button(
            "📖 Knowledge Base",
            key="hero_learn",
            type="secondary",
            use_container_width=True,
        ):
            st.switch_page("pages/4_Knowledge_Base.py")
    with col_btn3:
        st.markdown("")  # spacer

    # Stats overview
    stats = get_dashboard_stats()
    st.markdown(
        '<div class="section-title">📊 Platform Overview</div>', unsafe_allow_html=True
    )
    stat_cols = st.columns(4)
    stat_items = [
        ("🔬", t("stats.total_scans"), stats["total_scans"], "#22C55E", 0),
        ("✅", t("stats.healthy"), stats["healthy_scans"], "#16A34A", 1),
        ("⚠️", t("stats.diseased"), stats["diseased_scans"], "#F59E0B", 2),
        ("🌾", t("stats.crops"), stats["total_crops"], "#3B82F6", 3),
    ]
    for i, (col, (icon, label, value, color, delay)) in enumerate(
        zip(stat_cols, stat_items)
    ):
        with col:
            render_stat_card(icon, label, f"{value:,}", color=color, delay=delay)

    # Quick actions and welcome card
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            '<div class="section-title">⚡ Quick Actions</div>', unsafe_allow_html=True
        )
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        quick_actions = [
            (
                "🔬",
                t("quick_action.detect"),
                t("quick_action.detect_desc"),
                "pages/2_Detection.py",
            ),
            (
                "📊",
                t("quick_action.analytics"),
                t("quick_action.analytics_desc"),
                "pages/3_Analytics.py",
            ),
            (
                "🌤️",
                t("quick_action.weather"),
                t("quick_action.weather_desc"),
                "pages/5_Weather.py",
            ),
            (
                "📖",
                t("quick_action.knowledge"),
                t("quick_action.knowledge_desc"),
                "pages/4_Knowledge_Base.py",
            ),
            (
                "📋",
                t("quick_action.history"),
                t("quick_action.history_desc"),
                "pages/6_History.py",
            ),
            (
                "🤖",
                t("quick_action.about"),
                t("quick_action.about_desc"),
                "pages/8_AI_Assistant.py",
            ),
        ]
        for icon, label, desc, _page in quick_actions:
            st.markdown(
                f"""
                <div class="feature-card glow-card">
                    <div style="font-size:1.8rem;margin-bottom:0.5rem;">{icon}</div>
                    <h4 style="font-weight:700;font-size:0.9rem;margin-bottom:0.25rem;color:var(--text);">{label}</h4>
                    <p style="font-size:0.8rem;color:var(--text-muted);margin:0;">{desc}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">💡 Tip</div>', unsafe_allow_html=True)
        render_card(
            icon="💡",
            title=t("tip.title"),
            content=f'<p style="color:var(--text-secondary);font-size:0.9rem;line-height:1.6;">{t("tip.description")}</p>',
        )

    # CTA Banner
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center;padding:2rem;margin-top:1rem;
             background:linear-gradient(135deg, rgba(34,197,94,0.10), rgba(59,130,246,0.06));
             border:1px solid var(--bg-glass-border);
             border-radius:var(--radius-xl);backdrop-filter:blur(20px);">
            <h3 style="font-weight:900;margin-bottom:0.5rem;font-size:1.3rem;
                background:linear-gradient(135deg, #22C55E, #3B82F6);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                {t("welcome.cta_title")}
            </h3>
            <p style="color:var(--text-secondary);font-size:0.95rem;">{t("welcome.cta_subtitle")}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def get_dashboard_stats():
    try:
        from database.db_manager import DatabaseManager

        db = DatabaseManager()
        stats = db.get_summary_stats()
        if stats["total_scans"] == 0:
            return {
                "total_scans": 0,
                "healthy_scans": 0,
                "diseased_scans": 0,
                "total_crops": 15,
                "most_common_disease": "N/A",
            }
        return stats
    except Exception:
        return {
            "total_scans": 0,
            "healthy_scans": 0,
            "diseased_scans": 0,
            "total_crops": 15,
            "most_common_disease": "N/A",
        }


def main():
    init_session_state()
    lang = st.session_state.get("language", "en")
    load_translations(lang)
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
