from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator, Sequence

import pytest
from ai.model_router import ModelRouter
from ai.provider_manager import AIProviderError, ProviderManager
from ai.settings import (
    AIProvider,
    AIProviderMode,
    ProviderConfig,
    coerce_mode,
    coerce_provider,
    get_default_base_url,
    get_default_model,
    is_openai_compatible,
    provider_from_env,
    validate_api_key,
)


class StreamingLocalProvider:
    def __init__(self, fail_stream: bool = False) -> None:
        self.fail_stream = fail_stream
        self.calls: list[str] = []

    def generate(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        self.calls.append(prompt)
        return f"local:{prompt}"

    async def generate_async(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        return self.generate(prompt, config, system_prompt, image_paths)

    def generate_stream(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> Generator[str, None, None]:
        if self.fail_stream:
            raise RuntimeError("stream failed")
        yield "hello"
        yield " world"

    async def generate_stream_async(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> AsyncGenerator[str, None]:
        for chunk in self.generate_stream(prompt, config, system_prompt, image_paths):
            yield chunk


class FailingCloudProvider:
    def generate(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        raise RuntimeError("cloud failed")

    async def generate_async(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        raise RuntimeError("async cloud failed")

    def generate_stream(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> Generator[str, None, None]:
        raise RuntimeError("cloud stream failed")


def test_provider_config_from_mapping_and_defaults() -> None:
    config = ProviderConfig.from_mapping(
        {
            "provider": "open_ai",
            "mode": "auto",
            "model": None,
            "base_url": "",
            "temperature": "9",
            "max_tokens": "99999",
            "timeout_seconds": "0",
            "retries": "9",
            "metadata": {"tenant": "farm-a"},
        }
    )

    assert config.provider == AIProvider.OPENAI
    assert config.mode == AIProviderMode.AUTO
    assert config.model == get_default_model(AIProvider.OPENAI)
    assert config.base_url == get_default_base_url(AIProvider.OPENAI)
    assert config.temperature == 2.0
    assert config.max_tokens == 32000
    assert config.timeout_seconds == 1.0
    assert config.retries == 5
    assert config.metadata == {"tenant": "farm-a"}


@pytest.mark.parametrize(
    ("provider", "expected"),
    [
        (AIProvider.ANTHROPIC, "claude-3-5-haiku-latest"),
        (AIProvider.GEMINI, "gemini-1.5-flash"),
        (AIProvider.GROQ, "llama-3.1-8b-instant"),
        (AIProvider.TOGETHER, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
        (AIProvider.OPENROUTER, "meta-llama/llama-3.1-8b-instruct"),
        (AIProvider.HUGGINGFACE, "mistralai/Mistral-7B-Instruct-v0.3"),
        (AIProvider.CUSTOM, "custom-model"),
    ],
)
def test_get_default_model_for_cloud_providers(
    provider: AIProvider, expected: str
) -> None:
    assert get_default_model(provider) == expected


def test_provider_aliases_and_validation() -> None:
    assert coerce_provider("hugging_face") == AIProvider.HUGGINGFACE
    assert coerce_mode("fallback") == AIProviderMode.AUTO
    assert is_openai_compatible(AIProvider.GROQ) is True
    assert validate_api_key(AIProvider.OLLAMA, "") == (
        True,
        "Local Ollama does not require an API key.",
    )
    assert validate_api_key(AIProvider.ANTHROPIC, "short")[0] is False
    assert validate_api_key(AIProvider.GEMINI, "bad")[0] is False
    assert validate_api_key(AIProvider.OPENAI, "bad-key")[0] is False


def test_provider_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_MODEL", "llama-test")
    monkeypatch.setenv("GROQ_API_KEY", "gq-test-key")
    monkeypatch.setenv("AI_TEMPERATURE", "0.7")

    config = provider_from_env()

    assert config.provider == AIProvider.GROQ
    assert config.mode == AIProviderMode.CLOUD
    assert config.model == "llama-test"
    assert config.api_key == "gq-test-key"
    assert config.temperature == 0.7


def test_model_router_auto_mode_with_and_without_key() -> None:
    local = StreamingLocalProvider()
    cloud = FailingCloudProvider()
    router = ModelRouter(local_provider=local, cloud_provider=cloud)

    assert (
        router.select(
            ProviderConfig(
                provider=AIProvider.OPENAI, mode=AIProviderMode.AUTO, api_key="x"
            )
        )[1]
        is cloud
    )
    assert (
        router.select(
            ProviderConfig(
                provider=AIProvider.OPENAI, mode=AIProviderMode.AUTO, api_key=""
            )
        )[1]
        is local
    )
    assert (
        router.select(
            ProviderConfig(
                provider=AIProvider.OPENAI, mode=AIProviderMode.CLOUD, api_key="x"
            )
        )[1]
        is cloud
    )


def test_provider_manager_async_cache_and_clear() -> None:
    local = StreamingLocalProvider()
    cloud = FailingCloudProvider()
    manager = ProviderManager(local_provider=local, cloud_provider=cloud)
    config = ProviderConfig(
        provider=AIProvider.OPENAI, mode=AIProviderMode.CLOUD, api_key="x"
    )

    response = asyncio.run(manager.generate_response_async("hello", config))
    cached = asyncio.run(manager.generate_response_async("hello", config))

    assert response.text == "local:hello"
    assert cached.cached is True
    manager.clear_cache()
    assert manager.generate_response("hello", config).cached is False


def test_provider_manager_streaming_and_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    local = StreamingLocalProvider()
    cloud = FailingCloudProvider()
    manager = ProviderManager(local_provider=local, cloud_provider=cloud)

    chunks = list(
        manager.generate_stream("hello", ProviderConfig(provider=AIProvider.OLLAMA))
    )
    assert [chunk.text for chunk in chunks] == ["hello", " world"]

    fallback_chunks = list(
        manager.generate_stream(
            "hello",
            ProviderConfig(
                provider=AIProvider.OPENAI, mode=AIProviderMode.CLOUD, api_key="x"
            ),
        )
    )
    assert [chunk.text for chunk in fallback_chunks] == ["hello", " world"]

    with pytest.raises(AIProviderError):
        list(
            manager.generate_stream(
                "hello",
                ProviderConfig(
                    provider=AIProvider.OPENAI, mode=AIProviderMode.CLOUD, api_key="x"
                ),
                fallback=False,
            )
        )
