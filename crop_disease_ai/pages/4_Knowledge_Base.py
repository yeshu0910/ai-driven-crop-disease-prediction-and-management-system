import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.translator import init_i18n, t

st.set_page_config(page_title=t("app.title") + " - " + t("nav.knowledge_base"), page_icon="📖", layout="wide")


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
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
        search_query = st.text_input(t("kb.search"), placeholder=t("kb.search_placeholder"))
    with col2:
        all_diseases = kb.get_all_diseases()
        crop_names = sorted({
            name.split(" ")[0] for name in all_diseases if " " in name
        })
        crop_filter = st.selectbox(t("kb.filter_crop"), [t("kb.all_crops")] + crop_names)
    return search_query, crop_filter


def render_disease_card(disease_name, info):
    severity = info.get("severity_indicators", {})
    severity_html = ""
    if severity:
        severity_html = f"<h4 style='margin-top: 1rem;'>{t('kb.severity_indicators')}</h4>"
        for level, desc in severity.items():
            color = {"Mild": "#f1c40f", "Moderate": "#e67e22", "Severe": "#e74c3c"}.get(level, "#333")
            level_label = t("severity." + level.lower()) if level.lower() in ["healthy", "mild", "moderate", "severe"] else level
            severity_html += f"""
                <div style="display:flex;align-items:center;margin:0.25rem 0;font-size:0.85rem;">
                    <span style="background:{color};color:white;padding:0.1rem 0.5rem;
                         border-radius:4px;font-size:0.7rem;font-weight:600;margin-right:0.5rem;flex-shrink:0;">
                        {level}
                    </span>
                    <span style="color:var(--text-secondary);">{desc}</span>
                </div>
            """

    affected = info.get("affected_crops", [])
    affected_text = ", ".join(affected) if affected else t("common.na")

    favorable = info.get("favorable_conditions", "N/A")

    st.markdown(f"""
        <div class="card" style="margin-bottom:1rem;padding:1.5rem;">
            <h3 class="gradient-text-primary" style="font-weight:700;margin-bottom:0.5rem;font-size:1.1rem;">
                {disease_name}
            </h3>
            <p style="color: #555; margin-bottom: 1rem; line-height: 1.6;">
                {info.get('description', t('kb.no_description'))}
            </p>

            <h4>{t('kb.symptoms')}</h4>
            <ul>
                {''.join(f'<li style="margin: 0.3rem 0;">{s}</li>' for s in info.get('symptoms', []))}
            </ul>

            <h4 style="margin-top: 1rem;">{t('kb.causes')}</h4>
            <ul>
                {''.join(f'<li style="margin: 0.3rem 0;">{c}</li>' for c in info.get('causes', []))}
            </ul>

            <h4 style="margin-top: 1rem;">{t('kb.prevention')}</h4>
            <ul>
                {''.join(f'<li style="margin: 0.3rem 0;">{p}</li>' for p in info.get('prevention', []))}
            </ul>

            <h4 style="margin-top: 1rem;">{t('kb.treatment')}</h4>
            <ul>
                {''.join(f'<li style="margin: 0.3rem 0;">{tr}</li>' for tr in info.get('treatment', []))}
            </ul>

            {severity_html}
            <p style="margin-top: 1rem;"><strong>{t('kb.affected_crops', crops=affected_text)}</strong></p>
            <p style="margin-top: 0.5rem;"><strong>{t('kb.favorable_conditions', conditions=favorable)}</strong></p>
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
