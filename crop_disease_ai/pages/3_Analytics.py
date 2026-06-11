import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
            <h1>📊 Analytics Dashboard</h1>
            <p>Comprehensive insights into crop health, disease patterns, and farm analytics</p>
        </div>
    """, unsafe_allow_html=True)


def render_summary_cards(stats):
    st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
    metrics = [
        ("🔬", "Total Scans", stats.get("total_scans", 0), "var(--primary)"),
        ("✅", "Healthy", stats.get("healthy_scans", 0), "var(--tertiary)"),
        ("⚠️", "Diseased", stats.get("diseased_scans", 0), "var(--accent-pink)"),
        ("🌾", "Crops Monitored", stats.get("total_crops", 0), "#818CF8"),
        ("🦠", "Common Disease", stats.get("most_common_disease", "N/A"), "#FB923C"),
    ]
    for icon, label, value, color in metrics:
        st.markdown(f"""
            <div class="stat-card animate-in">
                <div class="stat-icon">{icon}</div>
                <div class="stat-label">{label}</div>
                <div class="stat-value" style="font-size:1.2rem;color:{color};">{value}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_disease_frequency(db):
    st.markdown("<h3 class='section-title gradient-text'>🦠 Disease Frequency</h3>", unsafe_allow_html=True)
    freq_data = db.get_disease_frequency(limit=15)
    if freq_data:
        df = pd.DataFrame(freq_data)
        fig = px.bar(
            df, x="count", y="disease_name",
            orientation="h",
            color="disease_name",
            color_discrete_map={
                d: "#4caf50" if "healthy" in d.lower() else "#ff6f00"
                for d in df["disease_name"]
            },
            template="plotly_white",
            height=500,
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="Number of Cases",
            yaxis_title="",
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No disease data available yet. Start detecting to populate analytics.")


def render_monthly_trends(db):
    st.markdown("<h3 class='section-title gradient-text'>📈 Monthly Trends</h3>", unsafe_allow_html=True)
    trends = db.get_monthly_trends(months=12)
    if trends:
        df = pd.DataFrame(trends)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["month"], y=df["total"],
            mode="lines+markers", name="Total Scans",
            line=dict(color="#2e7d32", width=3),
            marker=dict(size=8),
        ))
        fig.add_trace(go.Bar(
            x=df["month"], y=df["healthy"],
            name="Healthy", marker_color="#4caf50", opacity=0.7,
        ))
        fig.add_trace(go.Bar(
            x=df["month"], y=df["diseased"],
            name="Diseased", marker_color="#ff6f00", opacity=0.7,
        ))
        fig.update_layout(
            barmode="stack",
            template="plotly_white",
            hovermode="x",
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.1),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Monthly trend data will appear as you perform disease detection scans.")


def render_crop_health_pie(db):
    st.markdown("<h3 class='section-title gradient-text'>🥧 Crop Health Distribution</h3>", unsafe_allow_html=True)
    stats = db.get_summary_stats()
    total = stats.get("total_scans", 0)
    healthy = stats.get("healthy_scans", 0)
    diseased = stats.get("diseased_scans", 0)
    if total > 0:
        fig = go.Figure(data=[go.Pie(
            labels=["Healthy", "Diseased"],
            values=[healthy, diseased],
            marker_colors=["#4caf50", "#ff6f00"],
            textinfo="label+percent",
            hole=0.4,
            pull=[0.05, 0],
        )])
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", y=1.1),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Health distribution will appear after first detection.")


def render_recent_detections(db):
    st.markdown("<h3 class='section-title gradient-text'>🕐 Recent Detections</h3>", unsafe_allow_html=True)
    predictions = db.get_all_predictions(limit=20)
    if predictions:
        data = []
        for p in predictions:
            created = p.get("created_at", "")
            if created and isinstance(created, str) and "T" in created:
                created = created.split(".")[0].replace("T", " ")
            data.append({
                "Date": created or "N/A",
                "Crop": p.get("crop_name", "N/A"),
                "Disease": p.get("disease_name", "N/A"),
                "Confidence": f"{p.get('confidence', 0)*100:.1f}%",
                "Severity": p.get("severity", "N/A"),
                "Risk": p.get("risk_level", "N/A"),
            })
        df = pd.DataFrame(data)
        st.dataframe(
            df, width='stretch', hide_index=True,
            column_config={
                "Date": st.column_config.TextColumn("Date", width="medium"),
                "Crop": st.column_config.TextColumn("Crop", width="small"),
                "Disease": st.column_config.TextColumn("Disease", width="medium"),
                "Confidence": st.column_config.TextColumn("Confidence", width="small"),
                "Severity": st.column_config.TextColumn("Severity", width="small"),
                "Risk": st.column_config.TextColumn("Risk", width="small"),
            },
        )
    else:
        st.info("No detection history yet. Go to the Detection page to analyze crops.")


def render_analytics_overview(db):
    st.markdown("<h3 class='section-title gradient-text'>📋 Daily Analytics Overview</h3>", unsafe_allow_html=True)
    analytics_data = db.get_analytics(days=30)
    if analytics_data:
        df = pd.DataFrame(analytics_data)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["total_scans"],
            mode="lines+markers", name="Total Scans",
            line=dict(color="#2e7d32", width=2),
            fill="tozeroy",
            fillcolor="rgba(46,125,50,0.1)",
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["healthy_scans"],
            mode="lines+markers", name="Healthy",
            line=dict(color="#4caf50", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["diseased_scans"],
            mode="lines+markers", name="Diseased",
            line=dict(color="#ff6f00", width=2),
        ))
        fig.update_layout(
            template="plotly_white",
            hovermode="x",
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.1),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Daily analytics will populate as you use the system.")


def main():
    load_css()
    render_header()

    try:
        db = get_db()
        stats = db.get_summary_stats()
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return

    render_summary_cards(stats)

    col1, col2 = st.columns([2, 1])
    with col1:
        render_monthly_trends(db)
    with col2:
        render_crop_health_pie(db)

    render_disease_frequency(db)

    col1, col2 = st.columns([1, 1])
    with col1:
        render_analytics_overview(db)
    with col2:
        st.markdown("<h3 class='section-title gradient-text'>💡 Insights</h3>", unsafe_allow_html=True)
        if stats["total_scans"] > 0:
            disease_pct = (stats["diseased_scans"] / stats["total_scans"]) * 100
            healthy_pct = (stats["healthy_scans"] / stats["total_scans"]) * 100
            st.markdown(f"""
                <div class="card">
                    <div class="info-box {'green' if healthy_pct > 50 else 'orange'}">
                        <strong>Crop Health Rate:</strong> {healthy_pct:.1f}%<br>
                        <strong>Disease Incidence:</strong> {disease_pct:.1f}%
                    </div>
                    <div class="info-box blue" style="margin-top:0.5rem;">
                        <strong>Most Common Disease:</strong> {stats.get('most_common_disease', 'N/A')}<br>
                        <strong>Cases:</strong> {stats.get('most_common_count', 0)}
                    </div>
                    <div class="info-box blue" style="margin-top:0.5rem;">
                        <strong>Crops Being Monitored:</strong> {stats.get('total_crops', 0)}<br>
                        <strong>Total Entries:</strong> {stats['total_scans']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Start detecting diseases to see insights.")

    render_recent_detections(db)

    if st.button("🔄 Refresh Analytics", type="primary", width='stretch'):
        st.rerun()


if __name__ == "__main__":
    main()
