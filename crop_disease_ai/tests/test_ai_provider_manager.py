from __future__ import annotations

from collections.abc import AsyncGenerator, Generator, Sequence
from pathlib import Path

from ai.provider_manager import AIResponse, ProviderManager
from ai.settings import (
    AIProvider,
    AIProviderMode,
    EncryptedProviderConfigStore,
    ProviderConfig,
    mask_api_key,
    validate_api_key,
)


class FakeLocalProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ProviderConfig]] = []

    def generate(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        self.calls.append((prompt, config))
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
        yield self.generate(prompt, config, system_prompt, image_paths)

    async def generate_stream_async(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> AsyncGenerator[str, None]:
        yield self.generate(prompt, config, system_prompt, image_paths)


class FakeCloudProvider:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[tuple[str, ProviderConfig]] = []

    def generate(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        self.calls.append((prompt, config))
        if self.fail:
            raise RuntimeError("simulated cloud failure")
        return f"cloud:{prompt}"

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
        yield self.generate(prompt, config, system_prompt, image_paths)

    async def generate_stream_async(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> AsyncGenerator[str, None]:
        yield self.generate(prompt, config, system_prompt, image_paths)


def cloud_config() -> ProviderConfig:
    return ProviderConfig(
        provider=AIProvider.OPENAI,
        mode=AIProviderMode.CLOUD,
        model="gpt-4o-mini",
        base_url="https://api.openai.com/v1",
        api_key="sk-test-key",
        temperature=0.3,
        max_tokens=128,
        enable_local_fallback=True,
    )


def test_provider_config_masks_api_key() -> None:
    config = cloud_config()
    assert config.redacted()["api_key"] == "sk-t...-key"
    assert mask_api_key("short") == "*****"


def test_api_key_validation_rejects_empty_cloud_key() -> None:
    is_valid, message = validate_api_key(AIProvider.OPENAI, "")
    assert not is_valid
    assert "required" in message


def test_provider_manager_routes_to_local_ollama() -> None:
    local = FakeLocalProvider()
    cloud = FakeCloudProvider()
    manager = ProviderManager(local_provider=local, cloud_provider=cloud)

    response = manager.generate_response("hello", ProviderConfig(provider=AIProvider.OLLAMA, mode=AIProviderMode.LOCAL))

    assert isinstance(response, AIResponse)
    assert response.text == "local:hello"
    assert response.provider == AIProvider.OLLAMA.value
    assert local.calls == [("hello", ProviderConfig(provider=AIProvider.OLLAMA, mode=AIProviderMode.LOCAL))]
    assert cloud.calls == []


def test_provider_manager_routes_to_cloud_provider() -> None:
    local = FakeLocalProvider()
    cloud = FakeCloudProvider()
    manager = ProviderManager(local_provider=local, cloud_provider=cloud)
    config = cloud_config()

    response = manager.generate_response("diagnose", config)

    assert response.text == "cloud:diagnose"
    assert response.provider == AIProvider.OPENAI.value
    assert cloud.calls == [("diagnose", config)]
    assert local.calls == []


def test_provider_manager_falls_back_to_local_provider() -> None:
    local = FakeLocalProvider()
    cloud = FakeCloudProvider(fail=True)
    manager = ProviderManager(local_provider=local, cloud_provider=cloud)

    response = manager.generate_response("fallback", cloud_config())

    assert response.text == "local:fallback"
    assert response.provider == AIProvider.OLLAMA.value
    assert response.metadata == {"fallback_from": AIProvider.OPENAI.value}
    assert len(local.calls) == 1
    assert len(cloud.calls) == 1


def test_provider_manager_caches_response() -> None:
    local = FakeLocalProvider()
    cloud = FakeCloudProvider()
    manager = ProviderManager(local_provider=local, cloud_provider=cloud)
    config = cloud_config()

    first = manager.generate_response("cached", config)
    second = manager.generate_response("cached", config)

    assert first.text == "cloud:cached"
    assert second.cached is True
    assert second.text == first.text
    assert len(cloud.calls) == 1


def test_encrypted_provider_config_store_round_trip(tmp_path: Path) -> None:
    store = EncryptedProviderConfigStore(tmp_path / "provider.enc")
    config = cloud_config()

    store.save(config, "test-encryption-key")
    loaded = store.load("test-encryption-key")

    assert loaded.provider == config.provider
    assert loaded.api_key == config.api_key
    assert loaded.model == config.model
