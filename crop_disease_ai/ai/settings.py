from __future__ import annotations

import base64
import hashlib
import importlib
import json
import os
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

_fernet_module: Any | None
try:
    _fernet_module = importlib.import_module("cryptography.fernet")
except ImportError:  # pragma: no cover - optional at runtime in restricted environments
    _fernet_module = None

_Fernet: type[Any] | None = (
    _fernet_module.Fernet if _fernet_module is not None else None
)


class AIProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"
    TOGETHER = "together"
    OPENROUTER = "openrouter"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class AIProviderMode(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    AUTO = "auto"


LOCAL_MODELS: tuple[str, ...] = (
    "llama3",
    "llama3.1",
    "mistral",
    "phi3",
    "gemma",
    "codellama",
)

OPENAI_COMPATIBLE_PROVIDERS: frozenset[AIProvider] = frozenset(
    {
        AIProvider.OPENAI,
        AIProvider.GROQ,
        AIProvider.TOGETHER,
        AIProvider.OPENROUTER,
    }
)

DEFAULT_PROVIDER_URLS: dict[AIProvider, str] = {
    AIProvider.OLLAMA: "http://localhost:11434",
    AIProvider.OPENAI: "https://api.openai.com/v1",
    AIProvider.ANTHROPIC: "https://api.anthropic.com/v1",
    AIProvider.GEMINI: "https://generativelanguage.googleapis.com/v1beta",
    AIProvider.GROQ: "https://api.groq.com/openai/v1",
    AIProvider.TOGETHER: "https://api.together.xyz/v1",
    AIProvider.OPENROUTER: "https://openrouter.ai/api/v1",
    AIProvider.HUGGINGFACE: "https://api-inference.huggingface.co",
    AIProvider.CUSTOM: "",
}

PROVIDER_ENV_KEYS: dict[AIProvider, str] = {
    AIProvider.OPENAI: "OPENAI_API_KEY",
    AIProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
    AIProvider.GEMINI: "GEMINI_API_KEY",
    AIProvider.GROQ: "GROQ_API_KEY",
    AIProvider.TOGETHER: "TOGETHER_API_KEY",
    AIProvider.OPENROUTER: "OPENROUTER_API_KEY",
    AIProvider.HUGGINGFACE: "HUGGINGFACE_API_KEY",
    AIProvider.CUSTOM: "CUSTOM_API_KEY",
}

PROVIDER_MODEL_ENV_KEYS: dict[AIProvider, str] = {
    AIProvider.OPENAI: "OPENAI_MODEL",
    AIProvider.ANTHROPIC: "ANTHROPIC_MODEL",
    AIProvider.GEMINI: "GEMINI_MODEL",
    AIProvider.GROQ: "GROQ_MODEL",
    AIProvider.TOGETHER: "TOGETHER_MODEL",
    AIProvider.OPENROUTER: "OPENROUTER_MODEL",
    AIProvider.HUGGINGFACE: "HUGGINGFACE_MODEL",
    AIProvider.CUSTOM: "CUSTOM_MODEL",
}

_PROVIDER_ALIASES: dict[str, AIProvider] = {
    "local": AIProvider.OLLAMA,
    "local_ollama": AIProvider.OLLAMA,
    "ollama_local": AIProvider.OLLAMA,
    "open_ai": AIProvider.OPENAI,
    "openai": AIProvider.OPENAI,
    "google_gemini": AIProvider.GEMINI,
    "gemini_google": AIProvider.GEMINI,
    "hf": AIProvider.HUGGINGFACE,
    "hugging_face": AIProvider.HUGGINGFACE,
    "huggingface": AIProvider.HUGGINGFACE,
    "huggingface_inference_api": AIProvider.HUGGINGFACE,
    "custom_endpoint": AIProvider.CUSTOM,
    "custom": AIProvider.CUSTOM,
}

_MODE_ALIASES: dict[str, AIProviderMode] = {
    "local_ai": AIProviderMode.LOCAL,
    "cloud_ai": AIProviderMode.CLOUD,
    "auto": AIProviderMode.AUTO,
    "fallback": AIProviderMode.AUTO,
}


@dataclass(frozen=True)
class ProviderConfig:
    provider: AIProvider | str = AIProvider.OLLAMA
    mode: AIProviderMode | str = AIProviderMode.LOCAL
    model: str = "llama3"
    base_url: str = DEFAULT_PROVIDER_URLS[AIProvider.OLLAMA]
    api_key: str = ""
    temperature: float = 0.2
    max_tokens: int = 1024
    timeout_seconds: float = 60.0
    retries: int = 2
    enable_local_fallback: bool = True
    cache_enabled: bool = True
    stream: bool = False
    system_prompt: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, object] | None) -> ProviderConfig:
        if not data:
            return cls()

        provider = coerce_provider(data.get("provider", AIProvider.OLLAMA))
        mode = coerce_mode(data.get("mode", _default_mode_for_provider(provider)))
        base_url = str(data.get("base_url") or get_default_base_url(provider)).strip()
        model = str(data.get("model") or _default_model_for_provider(provider)).strip()
        api_key = str(data.get("api_key") or os.getenv("AI_API_KEY") or "").strip()
        temperature = _bounded_float(data.get("temperature"), 0.0, 2.0, 0.2)
        max_tokens = _bounded_int(data.get("max_tokens"), 1, 32_000, 1024)
        timeout_seconds = _bounded_float(data.get("timeout_seconds"), 1.0, 300.0, 60.0)
        retries = _bounded_int(data.get("retries"), 0, 5, 2)

        return cls(
            provider=provider,
            mode=mode,
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            retries=retries,
            enable_local_fallback=bool(data.get("enable_local_fallback", True)),
            cache_enabled=bool(data.get("cache_enabled", True)),
            stream=bool(data.get("stream", False)),
            system_prompt=str(data.get("system_prompt") or ""),
            metadata=_string_metadata(data.get("metadata", {})),
        )

    def to_dict(self, include_secret: bool = False) -> dict[str, object]:
        data = asdict(self)
        if not include_secret and self.api_key:
            data["api_key"] = mask_api_key(self.api_key)
        elif not include_secret:
            data["api_key"] = ""
        return data

    def redacted(self) -> dict[str, object]:
        return self.to_dict(include_secret=False)


def coerce_provider(value: object) -> AIProvider:
    if isinstance(value, AIProvider):
        return value
    normalized = _normalize_key(str(value))
    provider = _PROVIDER_ALIASES.get(normalized)
    if provider is not None:
        return provider
    return AIProvider(normalized)


def coerce_mode(value: object) -> AIProviderMode:
    if isinstance(value, AIProviderMode):
        return value
    normalized = _normalize_key(str(value))
    mode = _MODE_ALIASES.get(normalized)
    if mode is not None:
        return mode
    return AIProviderMode(normalized)


def get_default_base_url(provider: AIProvider | str) -> str:
    provider_value = coerce_provider(provider)
    return DEFAULT_PROVIDER_URLS.get(provider_value, "")


def get_default_model(provider: AIProvider | str) -> str:
    provider_value = coerce_provider(provider)
    if provider_value == AIProvider.OPENAI:
        return "gpt-4o-mini"
    if provider_value == AIProvider.ANTHROPIC:
        return "claude-3-5-haiku-latest"
    if provider_value == AIProvider.GEMINI:
        return "gemini-1.5-flash"
    if provider_value == AIProvider.GROQ:
        return "llama-3.1-8b-instant"
    if provider_value == AIProvider.TOGETHER:
        return "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    if provider_value == AIProvider.OPENROUTER:
        return "meta-llama/llama-3.1-8b-instruct"
    if provider_value == AIProvider.HUGGINGFACE:
        return "mistralai/Mistral-7B-Instruct-v0.3"
    if provider_value == AIProvider.CUSTOM:
        return "custom-model"
    return "llama3"


def is_openai_compatible(provider: AIProvider | str) -> bool:
    return coerce_provider(provider) in OPENAI_COMPATIBLE_PROVIDERS


def mask_api_key(api_key: str) -> str:
    if not api_key:
        return ""
    stripped = api_key.strip()
    if len(stripped) <= 8:
        return "*" * min(len(stripped), 8)
    return f"{stripped[:4]}...{stripped[-4:]}"


def validate_api_key(provider: AIProvider | str, api_key: str) -> tuple[bool, str]:
    provider_value = coerce_provider(provider)
    if provider_value == AIProvider.OLLAMA:
        return True, "Local Ollama does not require an API key."

    stripped = api_key.strip()
    if not stripped:
        return False, "API key is required for cloud providers."
    if len(stripped) < 8:
        return False, "API key looks too short."

    if provider_value == AIProvider.ANTHROPIC and not stripped.startswith("sk-ant-"):
        return False, "Anthropic API keys usually start with sk-ant-."
    if provider_value == AIProvider.GEMINI and not re.match(
        r"^[A-Za-z0-9_-]{20,}$", stripped
    ):
        return (
            False,
            "Gemini API keys usually contain letters, numbers, underscores, or hyphens.",
        )
    if provider_value == AIProvider.OPENAI and not stripped.startswith(
        ("sk-", "svproj-")
    ):
        return False, "OpenAI API keys usually start with sk- or svproj-."
    return True, "API key format looks valid."


def provider_from_env() -> ProviderConfig:
    provider = coerce_provider(os.getenv("AI_PROVIDER", "ollama"))
    mode = coerce_mode(
        os.getenv("AI_PROVIDER_MODE", _default_mode_for_provider(provider))
    )
    model = os.getenv("AI_MODEL") or os.getenv(
        PROVIDER_MODEL_ENV_KEYS.get(provider, "AI_MODEL")
    )
    base_url = (
        os.getenv("AI_BASE_URL")
        or os.getenv("OLLAMA_BASE_URL")
        or get_default_base_url(provider)
    )
    api_key = os.getenv("AI_API_KEY") or os.getenv(
        PROVIDER_ENV_KEYS.get(provider, "AI_API_KEY"), ""
    )

    return ProviderConfig.from_mapping(
        {
            "provider": provider,
            "mode": mode,
            "model": model or get_default_model(provider),
            "base_url": base_url,
            "api_key": api_key,
            "temperature": os.getenv("AI_TEMPERATURE", "0.2"),
            "max_tokens": os.getenv("AI_MAX_TOKENS", "1024"),
            "timeout_seconds": os.getenv("AI_TIMEOUT_SECONDS", "60"),
            "retries": os.getenv("AI_RETRIES", "2"),
            "enable_local_fallback": os.getenv("AI_ENABLE_LOCAL_FALLBACK", "true"),
            "cache_enabled": os.getenv("AI_CACHE_ENABLED", "true"),
            "stream": os.getenv("AI_STREAM", "false"),
            "system_prompt": os.getenv("AI_SYSTEM_PROMPT", ""),
        }
    )


class EncryptedProviderConfigStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = (
            Path(path)
            if path
            else Path.home() / ".crop_disease_ai" / "provider_config.enc"
        )

    def save(self, config: ProviderConfig, encryption_key: str) -> None:
        fernet = self._get_fernet(encryption_key)
        payload = json.dumps(
            config.to_dict(include_secret=True), sort_keys=True
        ).encode("utf-8")
        encrypted = fernet.encrypt(payload)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(encrypted)
        self.path.chmod(0o600)

    def load(self, encryption_key: str) -> ProviderConfig:
        fernet = self._get_fernet(encryption_key)
        if not self.path.exists():
            return ProviderConfig()
        encrypted = self.path.read_bytes()
        decrypted = fernet.decrypt(encrypted)
        return ProviderConfig.from_mapping(json.loads(decrypted.decode("utf-8")))

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()

    @staticmethod
    def _get_fernet(encryption_key: str) -> Any:
        if _Fernet is None:
            raise RuntimeError(
                "cryptography is required for encrypted provider config storage."
            )
        key_material = encryption_key.strip().encode("utf-8")
        digest = hashlib.sha256(key_material).digest()
        fernet_key = base64.urlsafe_b64encode(digest)
        return _Fernet(fernet_key)


def _default_mode_for_provider(provider: AIProvider) -> AIProviderMode:
    return (
        AIProviderMode.LOCAL if provider == AIProvider.OLLAMA else AIProviderMode.CLOUD
    )


def _default_model_for_provider(provider: AIProvider) -> str:
    return get_default_model(provider)


def _normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _bounded_float(
    value: object, minimum: float, maximum: float, default: float
) -> float:
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return min(max(parsed, minimum), maximum)


def _bounded_int(value: object, minimum: int, maximum: int, default: int) -> int:
    try:
        parsed = int(str(value))
    except (TypeError, ValueError):
        return default
    return min(max(parsed, minimum), maximum)


def _string_metadata(value: object) -> dict[str, str]:
    if isinstance(value, Mapping):
        return {str(k): str(v) for k, v in value.items()}
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            if isinstance(parsed, Mapping):
                return {str(k): str(v) for k, v in parsed.items()}
        except json.JSONDecodeError:
            return {}
    return {}


__all__ = [
    "AIProvider",
    "AIProviderMode",
    "EncryptedProviderConfigStore",
    "LOCAL_MODELS",
    "OPENAI_COMPATIBLE_PROVIDERS",
    "ProviderConfig",
    "coerce_mode",
    "coerce_provider",
    "get_default_base_url",
    "get_default_model",
    "is_openai_compatible",
    "mask_api_key",
    "provider_from_env",
    "validate_api_key",
]
