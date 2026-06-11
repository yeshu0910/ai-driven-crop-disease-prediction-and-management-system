import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


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
    st.markdown("""
        <div class="main-header">
            <h1>📖 Disease Knowledge Base</h1>
            <p>Comprehensive information about crop diseases, symptoms, causes, and treatments</p>
        </div>
    """, unsafe_allow_html=True)


def render_search_and_filter(kb):
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input(
            "🔍 Search diseases, symptoms, or causes",
            placeholder="e.g., blight, leaf spot, fungal...",
        )
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
        severity_html = "<h4 style='margin-top:0.75rem;font-size:0.9rem;'>Severity Indicators</h4>"
        for level, desc in severity.items():
            color = {"Mild": "#f1c40f", "Moderate": "#e67e22", "Severe": "#e74c3c"}.get(level, "#333")
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
    favorable = info.get("favorable_conditions", "N/A")

    st.markdown(f"""
        <div class="card" style="margin-bottom:1rem;padding:1.5rem;">
            <h3 class="gradient-text-primary" style="font-weight:700;margin-bottom:0.5rem;font-size:1.1rem;">
                {disease_name}
            </h3>
            <p style="color:var(--text-secondary);margin-bottom:0.75rem;line-height:1.6;font-size:0.9rem;">
                {info.get('description', 'No description available.')}
            </p>

            <h4 style="font-size:0.9rem;margin-top:0.75rem;">Symptoms</h4>
            <ul style="font-size:0.85rem;color:var(--text-secondary);padding-left:1.25rem;">
                {''.join(f'<li style="margin:0.2rem 0;">{s}</li>' for s in info.get('symptoms', []))}
            </ul>

            <h4 style="font-size:0.9rem;margin-top:0.75rem;">Causes</h4>
            <ul style="font-size:0.85rem;color:var(--text-secondary);padding-left:1.25rem;">
                {''.join(f'<li style="margin:0.2rem 0;">{c}</li>' for c in info.get('causes', []))}
            </ul>

            <h4 style="font-size:0.9rem;margin-top:0.75rem;">Prevention</h4>
            <ul style="font-size:0.85rem;color:var(--text-secondary);padding-left:1.25rem;">
                {''.join(f'<li style="margin:0.2rem 0;">{p}</li>' for p in info.get('prevention', []))}
            </ul>

            <h4 style="font-size:0.9rem;margin-top:0.75rem;">Treatment</h4>
            <ul style="font-size:0.85rem;color:var(--text-secondary);padding-left:1.25rem;">
                {''.join(f'<li style="margin:0.2rem 0;">{t}</li>' for t in info.get('treatment', []))}
            </ul>

            {severity_html}

            <p style="margin-top:0.5rem;font-size:0.85rem;">
                <strong>Affected Crops:</strong> {', '.join(affected) if affected else 'See crop name'}
            </p>
            <p style="font-size:0.85rem;"><strong>Favorable Conditions:</strong> {favorable}</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    load_css()
    render_header()

    kb = get_knowledge_base()
    search_query, crop_filter = render_search_and_filter(kb)

    try:
        if crop_filter != "All Crops":
            diseases = kb.filter_by_crop(crop_filter)
        elif search_query:
            diseases = kb.search(search_query)
        else:
            diseases = kb.get_all_diseases()
    except Exception as e:
        st.error(f"Error retrieving disease data: {e}")
        return

    st.markdown(f"<p style='color:var(--text-muted);margin-bottom:0.75rem;font-size:0.85rem;'>Showing {len(diseases)} disease records</p>", unsafe_allow_html=True)

    for disease_name in diseases:
        info = kb.get_disease_info(disease_name)
        render_disease_card(disease_name, info)


if __name__ == "__main__":
    main()
