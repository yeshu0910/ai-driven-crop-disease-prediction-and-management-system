from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol

from ai.local_provider import OllamaLocalProvider
from ai.settings import AIProvider, AIProviderMode, ProviderConfig, coerce_mode, coerce_provider


class TextGenerator(Protocol):
    def generate(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        ...

    async def generate_async(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        ...

    def generate_stream(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> Iterator[str]:
        ...


class ModelRouter:
    def __init__(
        self,
        local_provider: TextGenerator | None = None,
        cloud_provider: TextGenerator | None = None,
    ) -> None:
        self.local_provider: TextGenerator
        if local_provider is None:
            self.local_provider = OllamaLocalProvider()
        else:
            self.local_provider = local_provider
        self.cloud_provider = cloud_provider

    def select(
        self,
        config: ProviderConfig,
    ) -> tuple[str, TextGenerator]:
        provider = coerce_provider(config.provider)
        mode = coerce_mode(config.mode)

        if mode == AIProviderMode.LOCAL or provider == AIProvider.OLLAMA:
            return AIProvider.OLLAMA.value, self.local_provider

        if mode == AIProviderMode.CLOUD:
            return provider.value, self._require_cloud_provider(provider)

        if config.api_key:
            return provider.value, self._require_cloud_provider(provider)

        return AIProvider.OLLAMA.value, self.local_provider

    def _require_cloud_provider(self, provider: AIProvider) -> TextGenerator:
        if self.cloud_provider is None:
            raise RuntimeError(f"Cloud provider {provider.value} was requested but no cloud provider is configured.")
        return self.cloud_provider
