import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.translator import init_i18n, t

st.set_page_config(page_title="Weather Intelligence - Crop Disease AI", page_icon="🌤️", layout="wide")


def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_weather_api():
    from utils.weather_api import WeatherAPI
    return WeatherAPI()


@st.cache_resource
def get_risk_predictor():
    from utils.risk_predictor import RiskPredictor
    from utils.weather_api import WeatherAPI
    return RiskPredictor(weather_api=WeatherAPI())


@st.cache_resource
def get_db():
    from database.db_manager import DatabaseManager
    return DatabaseManager()


def render_header():
    st.markdown(f"""
        <div class="main-header">
            <h1>{t('weather.title')}</h1>
            <p>{t('weather.subtitle')}</p>
        </div>
    """, unsafe_allow_html=True)


def render_current_weather(weather_data):
    if not weather_data:
        st.warning(t("weather.fetch_error"))
        return

    source_badge = t("weather.source_live") if weather_data.get("source") == "api" else t("weather.source_simulated")
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h3 style="margin: 0;">📍 {weather_data.get('location', 'Unknown')}</h3>
            <span style="font-size: 0.8rem; color: #888;">{source_badge}</span>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    metrics = [
        ("🌡️", t("weather.metric_temp"), f"{weather_data.get('temperature', 'N/A')}°C", "#e53935"),
        ("💧", t("weather.metric_humidity"), f"{weather_data.get('humidity', 'N/A')}%", "#1e88e5"),
        ("💨", t("weather.metric_wind"), f"{weather_data.get('wind_speed', 'N/A')} m/s", "#43a047"),
        ("☁️", t("weather.metric_condition"), weather_data.get('weather_description', 'N/A').title(), "#fb8c00"),
        ("🌊", t("weather.metric_pressure"), f"{weather_data.get('pressure', 'N/A')} hPa", "#8e24aa")
    ]
    for i, (icon, label, value, color) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
                <div class="dashboard-card" style="text-align: center;">
                    <div style="font-size: 1.5rem;">{icon}</div>
                    <div class="card-label">{label}</div>
                    <div class="card-value" style="font-size: 1.2rem; color: {color};">{value}</div>
                </div>
            """, unsafe_allow_html=True)


def render_forecast(forecast_data):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('weather.forecast_title')}</h3>", unsafe_allow_html=True)

    if not forecast_data or "forecasts" not in forecast_data:
        st.info(t("weather.forecast_unavailable"))
        return

    forecasts = forecast_data["forecasts"]

    df = pd.DataFrame(forecasts)
    df["date_display"] = pd.to_datetime(df["date"]).dt.strftime("%a<br>%d %b")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["temp_max"],
        mode="lines+markers",
        name=t("analytics.chart_temp_max"),
        line=dict(color="#e53935", width=2),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["temp_min"],
        mode="lines+markers",
        name=t("analytics.chart_temp_min"),
        line=dict(color="#1e88e5", width=2),
        marker=dict(size=6),
        fill="tonexty",
        fillcolor="rgba(30,136,229,0.1)"
    ))
    fig.update_layout(
        title=t("weather.forecast_temp"),
        template="plotly_white",
        hovermode="x",
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=1.1),
        xaxis=dict(showgrid=False),
        yaxis=dict(title=t("weather.metric_temp"))
    )
    st.plotly_chart(fig, width='stretch')

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df["date"], y=df["humidity_avg"],
        name=t("weather.metric_humidity"),
        marker_color="#1e88e5",
        opacity=0.7,
        text=df["humidity_avg"].round(1),
        textposition="outside"
    ))
    fig2.add_trace(go.Scatter(
        x=df["date"], y=df["wind_speed_avg"],
        mode="lines+markers",
        name=t("weather.metric_wind"),
        line=dict(color="#43a047", width=2),
        marker=dict(size=6),
        yaxis="y2"
    ))
    fig2.update_layout(
        title=t("weather.forecast_humidity_wind"),
        template="plotly_white",
        hovermode="x",
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=1.1),
        xaxis=dict(showgrid=False),
        yaxis=dict(title=t("weather.metric_humidity")),
        yaxis2=dict(title=t("weather.metric_wind"), overlaying="y", side="right")
    )
    st.plotly_chart(fig2, width='stretch')


def render_disease_risk(risk_prediction, crop_name):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('weather.risk_title')}</h3>", unsafe_allow_html=True)

    if not risk_prediction or "predictions" not in risk_prediction:
        st.info(t("weather.risk_select_prompt"))
        return

    overall = risk_prediction.get("overall_risk", {})
    risk_level = overall.get("risk_level", "Unknown")
    risk_score = overall.get("risk_score", 0)

    risk_color = {"Low": "#4caf50", "Medium": "#ff6f00", "High": "#e53935", "Unknown": "#888"}.get(risk_level, "#888")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
            <div class="dashboard-card" style="text-align: center;">
                <div style="font-size: 3rem; color: {risk_color}; font-weight: 800;">
                    {risk_level}
                </div>
                <div class="card-label">{t('weather.risk_overall')}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {risk_color};">
                    {risk_score:.1f}%
                </div>
                <div style="margin-top: 0.5rem;">
                    <span style="font-size: 0.85rem;">
                        ⚠️ {t('weather.risk_high_days', count=risk_prediction.get('high_risk_days', 0))}<br>
                        🟡 {t('weather.risk_medium_days', count=risk_prediction.get('medium_risk_days', 0))}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        predictions = risk_prediction.get("predictions", [])
        if predictions:
            df = pd.DataFrame(predictions)
            color_map = {"Low": "#4caf50", "Medium": "#ff6f00", "High": "#e53935"}
            df["color"] = df["risk_level"].map(color_map)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["date"], y=df["risk_score"],
                marker_color=df["color"],
                text=df["risk_level"],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Risk: %{y:.1f}%<br>Level: %{text}<extra></extra>"
            ))
            fig.update_layout(
                title=t("weather.risk_daily", crop=crop_name),
                template="plotly_white",
                height=250,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(showgrid=False),
                yaxis=dict(title=t("weather.risk_score"), range=[0, 110])
            )
            st.plotly_chart(fig, width='stretch')

    actions = risk_prediction.get("preventive_actions", [])
    if actions:
        with st.expander(t("weather.risk_preventive"), expanded=True):
            for action in actions:
                st.markdown(f"- {action}")


def render_weather_history(db):
    st.markdown(f"<h3 style='margin: 1.5rem 0 1rem;'>{t('weather.history_title')}</h3>", unsafe_allow_html=True)
    logs = db.get_weather_logs(limit=20)

    if logs:
        df = pd.DataFrame(logs)
        df["logged_at_display"] = pd.to_datetime(df["logged_at"]).dt.strftime("%Y-%m-%d %H:%M")
        display_cols = ["logged_at_display", "temperature", "humidity", "wind_speed", "weather_description"]
        display_df = df[display_cols].rename(columns={
            "logged_at_display": t("weather.table_time"),
            "temperature": t("weather.table_temp"),
            "humidity": t("weather.table_humidity"),
            "wind_speed": t("weather.table_wind"),
            "weather_description": t("weather.table_conditions")
        })
        st.dataframe(display_df, width='stretch', hide_index=True)
    else:
        st.info(t("weather.no_logs"))


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    weather_api = get_weather_api()
    risk_predictor = get_risk_predictor()
    db = get_db()

    if not weather_api.is_configured():
        st.warning(t("weather.api_not_configured"))

    col1, col2 = st.columns([2, 1])
    with col1:
        location = st.text_input(t("weather.location_label"), placeholder=t("weather.location_placeholder"), help=t("weather.location_help"))
    with col2:
        from utils.config import SUPPORTED_CROPS
        crop_name = st.selectbox(t("weather.crop_select"), SUPPORTED_CROPS, index=0)

    if st.button(t("weather.btn_update"), type="primary", width='stretch'):
        with st.spinner(t("weather.fetching")):
            weather_data = weather_api.get_current_weather(location)
            forecast_data = weather_api.get_forecast(location, days=7)

            if weather_data:
                db.log_weather(
                    location=weather_data.get("location", location),
                    temperature=weather_data.get("temperature"),
                    humidity=weather_data.get("humidity"),
                    pressure=weather_data.get("pressure"),
                    wind_speed=weather_data.get("wind_speed"),
                    weather_description=weather_data.get("weather_description")
                )

            st.session_state["weather_data"] = weather_data
            st.session_state["forecast_data"] = forecast_data

            risk = risk_predictor.predict_7_day_risk(crop_name, forecast_data)
            st.session_state["risk_prediction"] = risk

            st.success(t("weather.updated_success"))

    weather_data = st.session_state.get("weather_data")
    forecast_data = st.session_state.get("forecast_data")
    risk_prediction = st.session_state.get("risk_prediction")

    if weather_data:
        render_current_weather(weather_data)

    if forecast_data:
        render_forecast(forecast_data)

    if risk_prediction:
        render_disease_risk(risk_prediction, crop_name)

    render_weather_history(db)


if __name__ == "__main__":
    main()
