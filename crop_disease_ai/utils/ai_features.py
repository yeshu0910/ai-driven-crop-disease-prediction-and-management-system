from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace

from ai.provider_manager import ProviderManager
from ai.settings import ProviderConfig

DEFAULT_SYSTEM_PROMPT = (
    "You are a precise agricultural AI assistant for crop disease prediction and management. "
    "Provide practical, safety-conscious guidance. Do not invent pesticide labels or dosages; "
    "when uncertain, recommend consulting a local agricultural extension officer."
)


class AIAssistantError(RuntimeError):
    pass


def chat_with_ai(
    messages: str,
    provider_config: ProviderConfig,
    manager: ProviderManager | None = None,
) -> str:
    prompt = f"Conversation history:\n{messages}\n\nAssistant response:"
    return _generate(
        prompt,
        provider_config,
        manager,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        max_tokens=1024,
    )


def summarize_text(
    text: str,
    provider_config: ProviderConfig,
    manager: ProviderManager | None = None,
    max_words: int = 150,
) -> str:
    prompt = (
        f"Summarize the following crop disease management text in at most {max_words} words. "
        "Use bullet points and keep farmer-facing language clear.\n\n{text}"
    )
    return _generate(
        prompt,
        provider_config,
        manager,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        max_tokens=512,
    )


def translate_text(
    text: str,
    target_language: str,
    provider_config: ProviderConfig,
    manager: ProviderManager | None = None,
) -> str:
    prompt = (
        f"Translate the following agricultural guidance to {target_language}. "
        "Preserve safety warnings and technical terms where needed.\n\n{text}"
    )
    return _generate(
        prompt,
        provider_config,
        manager,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        max_tokens=1024,
    )


def analyze_image_prediction(
    crop_name: str,
    disease_name: str,
    confidence: float,
    severity: str,
    visible_symptoms: Sequence[str],
    provider_config: ProviderConfig,
    manager: ProviderManager | None = None,
) -> str:
    symptoms = (
        "\n".join(f"- {symptom}" for symptom in visible_symptoms) or "- Not provided"
    )
    prompt = f"""
Crop: {crop_name}
Disease: {disease_name}
Confidence: {confidence * 100:.1f}%
Severity: {severity}

Visible symptoms:
{symptoms}

Explain this diagnosis in farmer-friendly language. Include likely causes, what to inspect next, and when to seek expert help.
"""
    return _generate(
        prompt,
        provider_config,
        manager,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        max_tokens=900,
    )


def generate_ai_recommendations(
    crop_name: str,
    disease_name: str,
    severity: str,
    infection_percentage: float,
    base_recommendations: Mapping[str, object],
    weather_data: Mapping[str, object] | None,
    provider_config: ProviderConfig,
    manager: ProviderManager | None = None,
) -> str:
    prompt = f"""
Crop: {crop_name}
Disease: {disease_name}
Severity: {severity}
Infection area: {infection_percentage:.1f}%

Base recommendations:
{_format_mapping(base_recommendations)}

Weather context:
{_format_mapping(weather_data or {})}

Create a concise, actionable management plan. Keep chemical, organic, irrigation, prevention, and safety guidance separate.
"""
    return _generate(
        prompt,
        provider_config,
        manager,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        max_tokens=1000,
    )


def generate_report_summary(
    report_data: Mapping[str, object],
    provider_config: ProviderConfig,
    manager: ProviderManager | None = None,
) -> str:
    prompt = f"""
Generate a concise diagnostic report summary for a farmer.

Report data:
{_format_mapping(report_data)}

Include diagnosis, confidence, severity, urgency, and the top 3 management actions.
"""
    return _generate(
        prompt,
        provider_config,
        manager,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        max_tokens=700,
    )


def _generate(
    prompt: str,
    provider_config: ProviderConfig,
    manager: ProviderManager | None,
    *,
    system_prompt: str,
    max_tokens: int,
) -> str:
    manager = manager or ProviderManager()
    config = _with_max_tokens(provider_config, max_tokens)
    try:
        response = manager.generate_response(
            prompt,
            config,
            system_prompt=system_prompt,
            fallback=True,
        )
    except Exception:
        return _static_fallback(prompt, system_prompt)
    return response.text.strip()


def _static_fallback(prompt: str, system_prompt: str) -> str:
    lower = prompt.lower()
    if "recommendation" in lower or "management plan" in lower or "actionable" in lower:
        return (
            "Management recommendations (static fallback):\n"
            "- Chemical: Apply recommended fungicide or bactericide per local label; rotate modes of action.\n"
            "- Organic: Use copper-based or neem oil sprays; ensure full leaf coverage.\n"
            "- Irrigation: Water at the base; avoid overhead irrigation to reduce humidity.\n"
            "- Prevention: Remove infected plant material, sanitize tools, and rotate crops.\n"
            "- Safety: Wear PPE, follow re-entry intervals, and consult a local agronomist."
        )
    if "summar" in lower:
        return "Summary (static fallback): Key points identified; review source text for specific details."
    if "translat" in lower:
        return "Translation (static fallback): Content not translatable without an active AI provider."
    if "explain" in lower or "diagnosis" in lower:
        return (
            "Diagnosis explanation (static fallback):\n"
            "The model detected abnormal symptoms. Inspect leaves for spots, yellowing, or lesions. "
            "Check soil moisture and recent weather. If symptoms worsen, consult a local extension officer."
        )
    if "chat" in lower or "conversation" in lower:
        return "I'm currently running in offline mode. Please check your AI provider configuration."
    return (
        "Response (static fallback):\n"
        "The AI assistant is unavailable right now. Please verify your Ollama setup or cloud API credentials."
    )


def _with_max_tokens(config: ProviderConfig, max_tokens: int) -> ProviderConfig:
    return replace(config, max_tokens=max_tokens)


def _format_mapping(data: Mapping[str, object]) -> str:
    if not data:
        return "N/A"
    lines = []
    for key, value in data.items():
        rendered = str(value)
        lines.append(f"- {key}: {rendered}")
    return "\n".join(lines)


__all__ = [
    "AIAssistantError",
    "DEFAULT_SYSTEM_PROMPT",
    "analyze_image_prediction",
    "chat_with_ai",
    "generate_ai_recommendations",
    "generate_report_summary",
    "summarize_text",
    "translate_text",
]
