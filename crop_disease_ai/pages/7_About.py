import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.translator import init_i18n, t

st.set_page_config(page_title="About - Crop Disease AI", page_icon="ℹ️", layout="wide")


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header():
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{t("about.title")}</h1>
            <p>{t("about.subtitle")}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            f"""
            <div class="dashboard-card" style="padding: 2rem;">
                <h2 style="color: #2e7d32; margin-bottom: 1rem;">{t("about.overview_title")}</h2>
                <p style="line-height: 1.7; font-size: 1.05rem;">
                    {t("about.overview_desc")}
                </p>
                <p style="line-height: 1.7; margin-top: 1rem;">
                    {t("about.overview_tech")}
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="dashboard-card" style="padding: 2rem; margin-top: 1.5rem;">
                <h2 style="color: #2e7d32; margin-bottom: 1rem;">{t("about.features_title")}</h2>
        """,
            unsafe_allow_html=True,
        )

        features = [
            ("🧠", t("about.feature_ai"), t("about.feature_ai_desc")),
            ("🌡️", t("about.feature_weather"), t("about.feature_weather_desc")),
            ("💊", t("about.feature_treatment"), t("about.feature_treatment_desc")),
            ("📊", t("about.feature_analytics"), t("about.feature_analytics_desc")),
            ("📄", t("about.feature_pdf"), t("about.feature_pdf_desc")),
            ("🔍", t("about.feature_xai"), t("about.feature_xai_desc")),
            ("🗄️", t("about.feature_db"), t("about.feature_db_desc")),
            ("📖", t("about.feature_kb"), t("about.feature_kb_desc")),
        ]
        for icon, title, desc in features:
            st.markdown(
                f"""
                <div style="display:flex;gap:0.75rem;margin:0.75rem 0;">
                    <div style="font-size:1.5rem;flex-shrink:0;">{icon}</div>
                    <div>
                        <h4 style="margin:0;font-weight:700;font-size:0.9rem;">{title}</h4>
                        <p style="margin:0.15rem 0 0;color:var(--text-secondary);font-size:0.85rem;">{desc}</p>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"""
            <div class="dashboard-card" style="padding: 2rem;">
                <h3 style="color: #2e7d32; margin-bottom: 1rem;">{t("about.tech_stack")}</h3>
        """,
            unsafe_allow_html=True,
        )
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
            st.markdown(
                f"""
                <div style="margin:0.4rem 0;font-size:0.85rem;">
                    <strong>{icon} {tech}</strong>
                    <div style="font-size:0.75rem;color:var(--text-muted);">{desc}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="dashboard-card" style="padding: 2rem; margin-top: 1.5rem;">
                <h3 style="color: #2e7d32; margin-bottom: 1rem;">{t("about.supported_crops")}</h3>
        """,
            unsafe_allow_html=True,
        )
        crops = [
            "Tomato",
            "Potato",
            "Rice",
            "Wheat",
            "Corn",
            "Cotton",
            "Soybean",
            "Sugarcane",
            "Groundnut",
            "Sunflower",
            "Banana",
            "Mango",
            "Grapes",
            "Apple",
            "Chili",
        ]
        for crop in crops:
            st.markdown(
                f"<div style='font-size:0.85rem;padding:0.1rem 0;'>{crop}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: #2e7d32; font-weight: 700;">{t("about.how_to_use")}</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="dashboard-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2.5rem;">1️⃣</div>
                <h4>{t("about.step1_title")}</h4>
                <p style="color: #666; font-size: 0.9rem;">
                    {t("about.step1_desc")}
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="dashboard-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2.5rem;">2️⃣</div>
                <h4>{t("about.step2_title")}</h4>
                <p style="color: #666; font-size: 0.9rem;">
                    {t("about.step2_desc")}
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="dashboard-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2.5rem;">3️⃣</div>
                <h4>{t("about.step3_title")}</h4>
                <p style="color: #666; font-size: 0.9rem;">
                    {t("about.step3_desc")}
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem; margin-top: 2rem;
             background: linear-gradient(135deg, #1b5e20, #2e7d32);
             border-radius: 16px; color: white;">
            <h3 style="font-weight: 700; margin-bottom: 0.5rem;">{t("about.cta_title")}</h3>
            <p style="opacity: 0.9; max-width: 600px; margin: 0 auto;">
                {t("about.cta_desc")}
            </p>
            <p style="margin-top: 1rem; opacity: 0.7; font-size: 0.9rem;">
                {t("about.footer")}
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
