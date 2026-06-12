from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from ai.settings import AIProvider, AIProviderMode, ProviderConfig
from utils.ai_features import (
    analyze_image_prediction,
    chat_with_ai,
    generate_ai_recommendations,
    generate_report_summary,
    summarize_text,
    translate_text,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_css() -> None:
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header() -> None:
    st.markdown("""
        <div class="main-header">
            <h1>AI Assistant</h1>
            <p>Unified local and BYOK AI tools for crop disease support</p>
        </div>
    """, unsafe_allow_html=True)


def get_session_config() -> ProviderConfig:
    return ProviderConfig(
        provider=str(st.session_state.get("ai_provider", AIProvider.OLLAMA.value)),
        mode=str(st.session_state.get("ai_mode", AIProviderMode.LOCAL.value)),
        model=str(st.session_state.get("ai_model", "llama3")),
        base_url=str(st.session_state.get("ai_base_url", "http://localhost:11434")),
        api_key=str(st.session_state.get("ai_api_key", "")),
        temperature=float(st.session_state.get("ai_temperature", 0.2)),
        max_tokens=int(st.session_state.get("ai_max_tokens", 1024)),
        timeout_seconds=float(st.session_state.get("ai_timeout_seconds", 60)),
        retries=int(st.session_state.get("ai_retries", 2)),
        enable_local_fallback=bool(st.session_state.get("ai_fallback_enabled", True)),
        cache_enabled=bool(st.session_state.get("ai_cache_enabled", True)),
        stream=bool(st.session_state.get("ai_stream_enabled", False)),
    )


def render_chat() -> None:
    st.subheader("Chatbot")
    if "ai_chat_messages" not in st.session_state:
        st.session_state["ai_chat_messages"] = [
            {"role": "assistant", "content": "Ask about crop disease diagnosis, treatment, or prevention."}
        ]

    for message in st.session_state["ai_chat_messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ask an agricultural AI question"):
        st.session_state["ai_chat_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"), st.spinner("Generating response..."):
            try:
                history = "\n".join(
                    f"{item['role']}: {item['content']}" for item in st.session_state["ai_chat_messages"][:-1]
                )
                response = chat_with_ai(history, get_session_config())
                st.session_state["ai_chat_messages"].append({"role": "assistant", "content": response})
                st.write(response)
            except Exception as exc:
                st.error(f"AI chat failed: {exc}")


def render_summarizer() -> None:
    st.subheader("Summarization")
    text = st.text_area("Text to summarize", height=140)
    if st.button("Summarize"):
        if not text.strip():
            st.warning("Enter text to summarize.")
            return
        with st.spinner("Summarizing..."):
            try:
                st.write(summarize_text(text, get_session_config()))
            except Exception as exc:
                st.error(f"Summarization failed: {exc}")


def render_translator() -> None:
    st.subheader("Translation")
    col1, col2 = st.columns([1, 2])
    with col1:
        target_language = st.text_input("Target language", value="Hindi")
    with col2:
        text = st.text_area("Text to translate", height=120)
    if st.button("Translate"):
        if not text.strip():
            st.warning("Enter text to translate.")
            return
        with st.spinner("Translating..."):
            try:
                st.write(translate_text(text, target_language, get_session_config()))
            except Exception as exc:
                st.error(f"Translation failed: {exc}")


def render_image_analysis() -> None:
    st.subheader("Image analysis explanation")
    last_result = st.session_state.get("last_result")
    if not last_result:
        st.info("Run Disease Detection first to generate an AI image explanation.")
        return

    symptoms = st.multiselect(
        "Visible symptoms",
        [
            "Leaf spots",
            "Yellowing",
            "Wilting",
            "Mold growth",
            "Necrotic lesions",
            "Stunted growth",
            "Fruit lesions",
        ],
    )
    if st.button("Generate AI image explanation"):
        with st.spinner("Analyzing diagnosis..."):
            try:
                explanation = analyze_image_prediction(
                    crop_name=str(last_result.get("crop_name", "Unknown")),
                    disease_name=str(last_result.get("disease_name", "Unknown")),
                    confidence=float(last_result.get("confidence", 0.0)),
                    severity=str(last_result.get("severity", "Unknown")),
                    visible_symptoms=symptoms,
                    provider_config=get_session_config(),
                )
                st.session_state["last_ai_image_explanation"] = explanation
                st.write(explanation)
            except Exception as exc:
                st.error(f"Image analysis failed: {exc}")

    if st.session_state.get("last_ai_image_explanation"):
        st.markdown(st.session_state["last_ai_image_explanation"])


def render_recommendations() -> None:
    st.subheader("Recommendation engine")
    last_result = st.session_state.get("last_result")
    crop_name = st.text_input("Crop", value=str(last_result.get("crop_name", "Tomato")) if last_result else "Tomato")
    disease_name = st.text_input("Disease", value=str(last_result.get("disease_name", "Early Blight")) if last_result else "Early Blight")
    severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"], index=1)
    infection_percentage = st.slider("Infection percentage", 0.0, 100.0, 25.0)
    weather = st.text_area("Weather context", value="Humidity 80%, rain expected tomorrow", height=80)

    if st.button("Generate AI recommendations"):
        base_recommendations = last_result.get("treatment", {}) if last_result else {}
        with st.spinner("Generating recommendations..."):
            try:
                plan = generate_ai_recommendations(
                    crop_name=crop_name,
                    disease_name=disease_name,
                    severity=severity,
                    infection_percentage=infection_percentage,
                    base_recommendations=base_recommendations,
                    weather_data={"manual_context": weather},
                    provider_config=get_session_config(),
                )
                st.session_state["last_ai_recommendations"] = plan
                st.write(plan)
            except Exception as exc:
                st.error(f"Recommendation generation failed: {exc}")

    if st.session_state.get("last_ai_recommendations"):
        st.markdown(st.session_state["last_ai_recommendations"])


def render_report_summary() -> None:
    st.subheader("Report generation")
    last_result = st.session_state.get("last_result")
    if not last_result:
        st.info("Run Disease Detection first to generate an AI report summary.")
        return

    report_data = {
        "crop_name": last_result.get("crop_name"),
        "disease_name": last_result.get("disease_name"),
        "confidence": last_result.get("confidence"),
        "severity": last_result.get("severity"),
        "risk_level": last_result.get("risk_level"),
        "infection_percentage": last_result.get("infection_percentage"),
    }
    if st.button("Generate report summary"):
        with st.spinner("Generating summary..."):
            try:
                summary = generate_report_summary(report_data, get_session_config())
                st.session_state["last_ai_report_summary"] = summary
                st.write(summary)
            except Exception as exc:
                st.error(f"Report summary failed: {exc}")

    if st.session_state.get("last_ai_report_summary"):
        st.markdown(st.session_state["last_ai_report_summary"])


def main() -> None:
    load_css()
    render_header()
    st.info("All AI features on this page call the unified provider_manager layer. Select Local (Ollama) or a BYOK provider in the sidebar.")
    render_chat()
    st.divider()
    render_summarizer()
    st.divider()
    render_translator()
    st.divider()
    render_image_analysis()
    st.divider()
    render_recommendations()
    st.divider()
    render_report_summary()


if __name__ == "__main__":
    main()
