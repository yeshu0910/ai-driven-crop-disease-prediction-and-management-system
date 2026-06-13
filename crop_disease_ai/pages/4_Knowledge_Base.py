import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.translator import init_i18n, t

st.set_page_config(
    page_title=t("app.title") + " - " + t("nav.knowledge_base"),
    page_icon="📖",
    layout="wide"
)


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_knowledge_base():
    from utils.disease_knowledge_base import DiseaseKnowledgeBase
    return DiseaseKnowledgeBase()


def render_header():
    st.markdown(f"""
    <div class="main-header">
        <h1>{t("kb.title")}</h1>
        <p>{t("kb.subtitle")}</p>
    </div>
    """, unsafe_allow_html=True)


def render_search_and_filter(kb):
    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input(t("kb.search_label"), placeholder=t("kb.search_placeholder"))
    with col2:
        all_diseases = kb.get_all_diseases()
        crop_names = sorted({
            name.split(" ")[0] for name in all_diseases if " " in name
        })
        crop_filter = st.selectbox(
            t("kb.filter_label"),
            [t("kb.filter_all")] + crop_names
        )

    return search_query, crop_filter


def render_disease_card(disease_name, info):
    severity = info.get("severity_indicators", {})
    severity_html = ""

    if severity:
        severity_html = f"<h4 style='margin-top:1rem;'>{t('kb.severity_indicators')}</h4>"

        for level, desc in severity.items():
            color = {
                "Mild": "#f1c40f",
                "Moderate": "#e67e22",
                "Severe": "#e74c3c"
            }.get(level, "#333")

            severity_html += f"""
            <div style="display:flex;align-items:center;margin:0.25rem 0;">
                <span style="background:{color};color:white;padding:0.1rem 0.5rem;
                border-radius:4px;font-size:0.7rem;font-weight:600;margin-right:0.5rem;">
                    {level}
                </span>
                <span>{desc}</span>
            </div>
            """

    affected = info.get("affected_crops", [])
    affected_text = ", ".join(affected) if affected else "N/A"
    favorable = info.get("favorable_conditions", "N/A")

    st.markdown(f"""
    <div class="card" style="margin-bottom:1rem;padding:1.5rem;">
        <h3>{disease_name}</h3>

        <p>{info.get('description', 'No description available')}</p>

        <h4>{t('kb.symptoms')}</h4>
        <ul>
            {''.join(f'<li>{x}</li>' for x in info.get('symptoms', []))}
        </ul>

        <h4>{t('kb.causes')}</h4>
        <ul>
            {''.join(f'<li>{x}</li>' for x in info.get('causes', []))}
        </ul>

        <h4>{t('kb.prevention')}</h4>
        <ul>
            {''.join(f'<li>{x}</li>' for x in info.get('prevention', []))}
        </ul>

        <h4>{t('kb.treatment')}</h4>
        <ul>
            {''.join(f'<li>{x}</li>' for x in info.get('treatment', []))}
        </ul>

        {severity_html}

        <p><strong>{t('kb.affected_crops')}:</strong> {affected_text}</p>
        <p><strong>{t('kb.favorable_conditions')}:</strong> {favorable}</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"

    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    kb = get_knowledge_base()
    search_query, crop_filter = render_search_and_filter(kb)

    if crop_filter != t("kb.filter_all"):
        diseases = kb.filter_by_crop(crop_filter)
    elif search_query:
        diseases = kb.search(search_query)
    else:
        diseases = kb.get_all_diseases()

    st.markdown(f"<p style='color:#888;margin-bottom:1rem;'>{t('kb.showing_records', count=len(diseases))}</p>", unsafe_allow_html=True)

    for disease_name in diseases:
        info = kb.get_disease_info(disease_name)
        render_disease_card(disease_name, info)


if __name__ == "__main__":
    main()
