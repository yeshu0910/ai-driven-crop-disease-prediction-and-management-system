import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(page_title="Knowledge Base - Crop Disease AI", page_icon="📖", layout="wide")


def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_knowledge_base():
    from utils.disease_knowledge_base import DiseaseKnowledgeBase
    return DiseaseKnowledgeBase()


def render_header():
    st.markdown("""
        <div class="main-header">
            <h1>📖 Disease Knowledge Base</h1>
            <p>Comprehensive information about crop diseases, symptoms, causes, and treatments</p>
        </div>
    """, unsafe_allow_html=True)


def render_search_and_filter(kb):
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 Search diseases, symptoms, or causes", placeholder="e.g., blight, leaf spot, fungal...")
    with col2:
        all_diseases = kb.get_all_diseases()
        crop_names = sorted(set(
            name.split(" ")[0] for name in all_diseases if " " in name
        ))
        crop_filter = st.selectbox("Filter by crop", ["All Crops"] + crop_names)
    return search_query, crop_filter


def render_disease_card(disease_name, info):
    severity = info.get("severity_indicators", {})
    severity_html = ""
    if severity:
        severity_html = "<h4 style='margin-top: 1rem;'>Severity Indicators</h4>"
        for level, desc in severity.items():
            color = {"Mild": "#f1c40f", "Moderate": "#e67e22", "Severe": "#e74c3c"}.get(level, "#333")
            severity_html += f"""
                <div style="display: flex; align-items: center; margin: 0.3rem 0;">
                    <span style="background: {color}; color: white; padding: 0.1rem 0.5rem;
                         border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-right: 0.5rem;">
                        {level}
                    </span>
                    <span style="font-size: 0.9rem;">{desc}</span>
                </div>
            """

    affected = info.get("affected_crops", [])
    affected_html = f"""
        <p><strong>Affected Crops:</strong> {', '.join(affected) if affected else 'See crop name'}</p>
    """

    favorable = info.get("favorable_conditions", "N/A")

    st.markdown(f"""
        <div class="dashboard-card" style="margin-bottom: 1.5rem; padding: 2rem;">
            <h3 style="color: #2e7d32; font-weight: 700; margin-bottom: 0.5rem;">
                {disease_name}
            </h3>
            <p style="color: #555; margin-bottom: 1rem; line-height: 1.6;">
                {info.get('description', 'No description available.')}
            </p>

            <h4>Symptoms</h4>
            <ul>
                {''.join(f'<li style="margin: 0.3rem 0;">{s}</li>' for s in info.get('symptoms', []))}
            </ul>

            <h4 style="margin-top: 1rem;">Causes</h4>
            <ul>
                {''.join(f'<li style="margin: 0.3rem 0;">{c}</li>' for c in info.get('causes', []))}
            </ul>

            <h4 style="margin-top: 1rem;">Prevention</h4>
            <ul>
                {''.join(f'<li style="margin: 0.3rem 0;">{p}</li>' for p in info.get('prevention', []))}
            </ul>

            <h4 style="margin-top: 1rem;">Treatment</h4>
            <ul>
                {''.join(f'<li style="margin: 0.3rem 0;">{t}</li>' for t in info.get('treatment', []))}
            </ul>

            {severity_html}
            <div style="margin-top: 1rem;">{affected_html}</div>
            <p style="margin-top: 0.5rem;"><strong>Favorable Conditions:</strong> {favorable}</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    load_css()
    render_header()

    kb = get_knowledge_base()
    search_query, crop_filter = render_search_and_filter(kb)

    if crop_filter != "All Crops":
        diseases = kb.filter_by_crop(crop_filter)
    elif search_query:
        diseases = kb.search(search_query)
    else:
        diseases = kb.get_all_diseases()

    st.markdown(f"<p style='color: #888; margin-bottom: 1rem;'>Showing {len(diseases)} disease records</p>", unsafe_allow_html=True)

    for disease_name in diseases:
        info = kb.get_disease_info(disease_name)
        render_disease_card(disease_name, info)


if __name__ == "__main__":
    main()
