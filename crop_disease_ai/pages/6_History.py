import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_db():
    from database.db_manager import DatabaseManager
    return DatabaseManager()


def render_header():
    st.markdown("""
        <div class="main-header">
            <h1>📋 Detection History</h1>
            <p>View and manage all crop disease detection records and reports</p>
        </div>
    """, unsafe_allow_html=True)


def render_filters():
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search by disease or crop...")
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Highest Confidence", "Lowest Confidence"],
        )
    with col3:
        filter_crop = st.text_input("🌾 Filter by crop", placeholder="e.g., Tomato")
    return search, sort_by, filter_crop


def render_predictions_table(predictions, search_query, sort_by, crop_filter):
    if not predictions:
        st.info("No detection records found. Start by detecting diseases on the Detection page.")
        return

    data = []
    for p in predictions:
        created = p.get("created_at", "")
        if created and isinstance(created, str) and "T" in created:
            created = created.split(".")[0].replace("T", " ")
        data.append({
            "id": p.get("id"),
            "Date": created or "N/A",
            "Crop": p.get("crop_name", "N/A"),
            "Disease": p.get("disease_name", "N/A"),
            "Confidence": p.get("confidence", 0),
            "Severity": p.get("severity", "N/A"),
            "Risk": p.get("risk_level", "N/A"),
            "Farmer": p.get("farmer_name", "N/A"),
        })

    df = pd.DataFrame(data)

    if search_query:
        mask = (
            df["Disease"].str.contains(search_query, case=False, na=False)
            | df["Crop"].str.contains(search_query, case=False, na=False)
        )
        df = df[mask]

    if crop_filter:
        df = df[df["Crop"].str.contains(crop_filter, case=False, na=False)]

    sort_map = {
        "Newest First": ("Date", False),
        "Oldest First": ("Date", True),
        "Highest Confidence": ("Confidence", False),
        "Lowest Confidence": ("Confidence", True),
    }
    if sort_by in sort_map:
        col, asc = sort_map[sort_by]
        df = df.sort_values(col, ascending=asc)

    st.markdown(f"<p style='color:var(--text-muted);font-size:0.85rem;'>Showing {len(df)} records</p>", unsafe_allow_html=True)

    for _, row in df.iterrows():
        confidence_val = row["Confidence"]
        confidence_pct = confidence_val * 100 if isinstance(confidence_val, float) else confidence_val
        severity = str(row["Severity"])
        sev_color = {"Healthy": "#4caf50", "Mild": "#f1c40f", "Moderate": "#e67e22", "Severe": "#e53935"}.get(severity, "#888")
        badge_class = "green" if severity in ("Healthy", "Mild") else "orange" if severity == "Moderate" else "red"

        st.markdown(f"""
            <div class="metric-card" style="border-left-color:{sev_color};">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
                    <div>
                        <strong style="font-size:1rem;">{row['Crop']}</strong> — {row['Disease']}
                    </div>
                    <span class="badge badge-{badge_class}">{severity}</span>
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:1.5rem;margin-top:0.4rem;font-size:0.8rem;color:var(--text-secondary);">
                    <span>📅 {row['Date']}</span>
                    <span>🎯 {confidence_pct:.1f}% confidence</span>
                    <span>⚠️ {row['Risk']} risk</span>
                    <span>👤 {row['Farmer']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    return df


def main():
    load_css()
    render_header()

    try:
        db = get_db()
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return

    search_query, sort_by, crop_filter = render_filters()
    predictions = db.get_all_predictions(limit=200)
    render_predictions_table(predictions, search_query, sort_by, crop_filter)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh", width='stretch'):
            st.rerun()
    with col2:
        if predictions and st.button("📥 Export to CSV", width='stretch'):
            data = []
            for p in predictions:
                created = p.get("created_at", "")
                if created and isinstance(created, str) and "T" in created:
                    created = created.split(".")[0].replace("T", " ")
                data.append({
                    "ID": p.get("id"),
                    "Date": created,
                    "Crop": p.get("crop_name"),
                    "Disease": p.get("disease_name"),
                    "Confidence": p.get("confidence"),
                    "Severity": p.get("severity"),
                    "Risk": p.get("risk_level"),
                    "Farmer": p.get("farmer_name"),
                })
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"disease_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch',
            )
    with col3:
        st.markdown("")


if __name__ == "__main__":
    main()
