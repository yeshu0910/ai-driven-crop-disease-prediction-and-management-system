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
            st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


@st.cache_resource
def get_knowledge_base():
    from utils.disease_knowledge_base import DiseaseKnowledgeBase
    return DiseaseKnowledgeBase()


def render_header():
    st.markdown('<div class="main-header"><h1>{}</h1><p>{}</p></div>'.format(t("kb.title"), t("kb.subtitle")), unsafe_allow_html=True)


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
        severity_html = '<h4 style="margin-top: 1rem;">{}</h4>'.format(t("kb.severity_indicators"))
        for level, desc in severity.items():
            color = {"Mild": "#f1c40f", "Moderate": "#e67e22", "Severe": "#e74c3c"}.get(level, "#333")
            severity_html += '<div style="display:flex;align-items:center;margin:0.25rem 0;font-size:0.85rem;"><span style="background:{};color:white;padding:0.1rem 0.5rem;border-radius:4px;font-size:0.7rem;font-weight:600;margin-right:0.5rem;flex-shrink:0;">{}</span><span style="color:#A1A1AA;">{}</span></div>'.format(color, level, desc)

    affected = info.get("affected_crops", [])
    affected_text = ", ".join(affected) if affected else t("common.na")

    favorable = info.get("favorable_conditions", "N/A")
    description = info.get("description", t("kb.no_description"))
    symptoms_list = "".join('<li style="margin: 0.3rem 0;">{}</li>'.format(s) for s in info.get("symptoms", []))
    causes_list = "".join('<li style="margin: 0.3rem 0;">{}</li>'.format(c) for c in info.get("causes", []))
    prevention_list = "".join('<li style="margin: 0.3rem 0;">{}</li>'.format(p) for p in info.get("prevention", []))
    treatment_list = "".join('<li style="margin: 0.3rem 0;">{}</li>'.format(tr) for tr in info.get("treatment", []))

    st.markdown(
        '<div class="card" style="margin-bottom:1rem;padding:1.5rem;"><h3 class="gradient-text-primary" style="font-weight:700;margin-bottom:0.5rem;font-size:1.1rem;">' + disease_name + '</h3><p style="color: #A1A1AA; margin-bottom: 1rem; line-height: 1.6;">' + description + '</p><h4 style="margin-top: 1rem;">' + t("kb.symptoms") + '</h4><ul>' + symptoms_list + '</ul><h4 style="margin-top: 1rem;">' + t("kb.causes") + '</h4><ul>' + causes_list + '</ul><h4 style="margin-top: 1rem;">' + t("kb.prevention") + '</h4><ul>' + prevention_list + '</ul><h4 style="margin-top: 1rem;">' + t("kb.treatment") + '</h4><ul>' + treatment_list + '</ul>' + severity_html + '<p style="margin-top: 1rem;"><strong>' + t("kb.affected_crops", crops=affected_text) + '</strong></p><p style="margin-top: 0.5rem;"><strong>' + t("kb.favorable_conditions", conditions=favorable) + '</strong></p></div>',
        unsafe_allow_html=True
    )


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    kb = get_knowledge_base()
    search_query, crop_filter = render_search_and_filter(kb)

    if crop_filter != t("kb.all_crops"):
        diseases = kb.filter_by_crop(crop_filter)
    elif search_query:
        diseases = kb.search(search_query)
    else:
        diseases = kb.get_all_diseases()

    st.markdown('<p style="color:#888;margin-bottom:1rem;">{}</p>'.format(t('kb.showing_records', count=len(diseases))), unsafe_allow_html=True)

    for disease_name in diseases:
        info = kb.get_disease_info(disease_name)
        render_disease_card(disease_name, info)


if __name__ == "__main__":
    main()
