from __future__ import annotations

import hashlib
import json
import logging
import time
from collections.abc import AsyncIterator, Iterator, Mapping, Sequence
from dataclasses import dataclass

from ai.cloud_provider import CloudProvider
from ai.local_provider import OllamaLocalProvider
from ai.model_router import ModelRouter, TextGenerator
from ai.settings import AIProvider, ProviderConfig, coerce_provider, provider_from_env

logger = logging.getLogger(__name__)


class AIProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class AIResponse:
    text: str
    provider: str
    model: str
    cached: bool = False
    latency_ms: float = 0.0
    metadata: dict[str, str] | None = None


class ProviderManager:
    def __init__(
        self,
        local_provider: TextGenerator | None = None,
        cloud_provider: TextGenerator | None = None,
        cache_ttl_seconds: int = 3600,
    ) -> None:
        local: TextGenerator = (
            OllamaLocalProvider() if local_provider is None else local_provider
        )
        cloud: TextGenerator = (
            CloudProvider() if cloud_provider is None else cloud_provider
        )

        self.router = ModelRouter(
            local_provider=local,
            cloud_provider=cloud,
        )
        self.cache_ttl_seconds = cache_ttl_seconds
        self._response_cache: dict[str, tuple[float, AIResponse]] = {}

    @classmethod
    def from_env(cls) -> ProviderManager:
        return cls()

    def generate_response(
        self,
        prompt: str,
        provider_config: ProviderConfig | Mapping[str, object] | None = None,
        *,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
        stream: bool = False,
        fallback: bool | None = None,
    ) -> AIResponse:
        config = self._normalize_config(provider_config)
        if stream:
            raise AIProviderError("Use generate_stream for streaming responses.")

        cache_key = self._cache_key(prompt, config, system_prompt, image_paths)
        if config.cache_enabled and cache_key in self._response_cache:
            cached_at, cached = self._response_cache[cache_key]
            if time.monotonic() - cached_at <= self.cache_ttl_seconds:
                return AIResponse(
                    text=cached.text,
                    provider=cached.provider,
                    model=cached.model,
                    cached=True,
                    latency_ms=0.0,
                    metadata=cached.metadata,
                )
            self._response_cache.pop(cache_key, None)

        started_at = time.perf_counter()
        selected_provider = coerce_provider(config.provider)
        response_metadata = dict(config.metadata)
        try:
            provider_name, generator = self.router.select(config)
            text = generator.generate(
                prompt,
                config,
                system_prompt=system_prompt,
                image_paths=image_paths,
            )
        except Exception as exc:
            if self._should_fallback(config, fallback, selected_provider):
                logger.warning(
                    "Primary AI provider failed; falling back to local Ollama."
                )
                local_config = self._local_config(config)
                provider_name = AIProvider.OLLAMA.value
                response_metadata = dict(local_config.metadata)
                text = self.router.local_provider.generate(
                    prompt,
                    local_config,
                    system_prompt=system_prompt,
                    image_paths=image_paths,
                )
            else:
                raise AIProviderError(
                    f"AI provider {selected_provider.value} failed."
                ) from exc

        latency_ms = (time.perf_counter() - started_at) * 1000
        response = AIResponse(
            text=text,
            provider=provider_name,
            model=config.model,
            cached=False,
            latency_ms=latency_ms,
            metadata=response_metadata,
        )
        if config.cache_enabled:
            self._response_cache[cache_key] = (time.monotonic(), response)
        return response

    async def generate_response_async(
        self,
        prompt: str,
        provider_config: ProviderConfig | Mapping[str, object] | None = None,
        *,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
        stream: bool = False,
        fallback: bool | None = None,
    ) -> AIResponse:
        config = self._normalize_config(provider_config)
        if stream:
            raise AIProviderError("Use generate_stream_async for streaming responses.")

        cache_key = self._cache_key(prompt, config, system_prompt, image_paths)
        if config.cache_enabled and cache_key in self._response_cache:
            cached_at, cached = self._response_cache[cache_key]
            if time.monotonic() - cached_at <= self.cache_ttl_seconds:
                return AIResponse(
                    text=cached.text,
                    provider=cached.provider,
                    model=cached.model,
                    cached=True,
                    latency_ms=0.0,
                    metadata=cached.metadata,
                )
            self._response_cache.pop(cache_key, None)

        started_at = time.perf_counter()
        selected_provider = coerce_provider(config.provider)
        response_metadata = dict(config.metadata)
        try:
            provider_name, generator = self.router.select(config)
            text = await generator.generate_async(
                prompt,
                config,
                system_prompt=system_prompt,
                image_paths=image_paths,
            )
        except Exception as exc:
            if self._should_fallback(config, fallback, selected_provider):
                logger.warning(
                    "Primary async AI provider failed; falling back to local Ollama."
                )
                local_config = self._local_config(config)
                provider_name = AIProvider.OLLAMA.value
                response_metadata = dict(local_config.metadata)
                text = await self.router.local_provider.generate_async(
                    prompt,
                    local_config,
                    system_prompt=system_prompt,
                    image_paths=image_paths,
                )
            else:
                raise AIProviderError(
                    f"Async AI provider {selected_provider.value} failed."
                ) from exc

        latency_ms = (time.perf_counter() - started_at) * 1000
        response = AIResponse(
            text=text,
            provider=provider_name,
            model=config.model,
            cached=False,
            latency_ms=latency_ms,
            metadata=response_metadata,
        )
        if config.cache_enabled:
            self._response_cache[cache_key] = (time.monotonic(), response)
        return response

    def generate_stream(
        self,
        prompt: str,
        provider_config: ProviderConfig | Mapping[str, object] | None = None,
        *,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
        fallback: bool | None = None,
    ) -> Iterator[AIResponse]:
        config = self._normalize_config(provider_config)
        provider_name, generator = self.router.select(config)
        try:
            if hasattr(generator, "generate_stream"):
                for chunk in generator.generate_stream(
                    prompt,
                    config,
                    system_prompt=system_prompt,
                    image_paths=image_paths,
                ):
                    yield AIResponse(
                        text=chunk,
                        provider=provider_name,
                        model=config.model,
                        cached=False,
                        latency_ms=0.0,
                        metadata=dict(config.metadata),
                    )
                return
        except Exception as exc:
            if self._should_fallback(
                config, fallback, coerce_provider(config.provider)
            ):
                logger.warning(
                    "Streaming AI provider failed; falling back to local Ollama."
                )
                local_config = self._local_config(config)
                for chunk in self.router.local_provider.generate_stream(
                    prompt,
                    local_config,
                    system_prompt=system_prompt,
                    image_paths=image_paths,
                ):
                    yield AIResponse(
                        text=chunk,
                        provider=AIProvider.OLLAMA.value,
                        model=local_config.model,
                        cached=False,
                        latency_ms=0.0,
                        metadata=dict(config.metadata),
                    )
                return
            raise AIProviderError(
                f"Streaming AI provider {coerce_provider(config.provider).value} failed."
            ) from exc

        response = self.generate_response(
            prompt,
            config,
            system_prompt=system_prompt,
            image_paths=image_paths,
            stream=False,
            fallback=fallback,
        )
        yield response

    async def generate_stream_async(
        self,
        prompt: str,
        provider_config: ProviderConfig | Mapping[str, object] | None = None,
        *,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
        fallback: bool | None = None,
    ) -> AsyncIterator[AIResponse]:
        config = self._normalize_config(provider_config)
        provider_name, generator = self.router.select(config)
        try:
            if hasattr(generator, "generate_stream"):
                for chunk in generator.generate_stream(
                    prompt,
                    config,
                    system_prompt=system_prompt,
                    image_paths=image_paths,
                ):
                    yield AIResponse(
                        text=chunk,
                        provider=provider_name,
                        model=config.model,
                        cached=False,
                        latency_ms=0.0,
                        metadata=dict(config.metadata),
                    )
                return
        except Exception as exc:
            if self._should_fallback(
                config, fallback, coerce_provider(config.provider)
            ):
                logger.warning(
                    "Async streaming AI provider failed; falling back to local Ollama."
                )
                local_config = self._local_config(config)
                for chunk in self.router.local_provider.generate_stream(
                    prompt,
                    local_config,
                    system_prompt=system_prompt,
                    image_paths=image_paths,
                ):
                    yield AIResponse(
                        text=chunk,
                        provider=AIProvider.OLLAMA.value,
                        model=local_config.model,
                        cached=False,
                        latency_ms=0.0,
                        metadata=dict(config.metadata),
                    )
                return
            raise AIProviderError(
                f"Async streaming AI provider {coerce_provider(config.provider).value} failed."
            ) from exc

        response = await self.generate_response_async(
            prompt,
            config,
            system_prompt=system_prompt,
            image_paths=image_paths,
            stream=False,
            fallback=fallback,
        )
        yield response

    def clear_cache(self) -> None:
        self._response_cache.clear()

    def _normalize_config(
        self,
        provider_config: ProviderConfig | Mapping[str, object] | None,
    ) -> ProviderConfig:
        if provider_config is None:
            return provider_from_env()
        if isinstance(provider_config, ProviderConfig):
            return provider_config
        return ProviderConfig.from_mapping(provider_config)

    def _cache_key(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str,
        image_paths: Sequence[str] | None,
    ) -> str:
        payload = {
            "provider": coerce_provider(config.provider).value,
            "mode": config.mode,
            "model": config.model,
            "base_url": config.base_url,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "system_prompt": system_prompt,
            "prompt": prompt,
            "image_paths": list(image_paths or []),
        }
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _should_fallback(
        config: ProviderConfig,
        fallback: bool | None,
        selected_provider: AIProvider,
    ) -> bool:
        if fallback is False:
            return False
        if fallback is True:
            return config.enable_local_fallback
        return config.enable_local_fallback and selected_provider != AIProvider.OLLAMA

    @staticmethod
    def _local_config(config: ProviderConfig) -> ProviderConfig:
        return ProviderConfig(
            provider=AIProvider.OLLAMA,
            mode="local",
            model=config.model if config.model else "llama3",
            base_url=config.base_url or "http://localhost:11434",
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout_seconds=config.timeout_seconds,
            retries=config.retries,
            enable_local_fallback=False,
            cache_enabled=config.cache_enabled,
            system_prompt=config.system_prompt,
            metadata={
                **config.metadata,
                "fallback_from": coerce_provider(config.provider).value,
            },
        )


_default_manager = ProviderManager()


def generate_response(
    prompt: str,
    provider_config: ProviderConfig | Mapping[str, object] | None = None,
    *,
    system_prompt: str = "",
    image_paths: Sequence[str] | None = None,
    stream: bool = False,
    fallback: bool | None = None,
) -> AIResponse:
    return _default_manager.generate_response(
        prompt,
        provider_config,
        system_prompt=system_prompt,
        image_paths=image_paths,
        stream=stream,
        fallback=fallback,
    )


def generate_stream(
    prompt: str,
    provider_config: ProviderConfig | Mapping[str, object] | None = None,
    *,
    system_prompt: str = "",
    image_paths: Sequence[str] | None = None,
    fallback: bool | None = None,
) -> Iterator[AIResponse]:
    return _default_manager.generate_stream(
        prompt,
        provider_config,
        system_prompt=system_prompt,
        image_paths=image_paths,
        fallback=fallback,
    )


__all__ = [
    "AIProviderError",
    "AIResponse",
    "ProviderManager",
    "generate_response",
    "generate_stream",
]
