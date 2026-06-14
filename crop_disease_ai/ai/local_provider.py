from __future__ import annotations

import json
import logging
from collections.abc import Iterator, Sequence

import httpx

from ai.settings import AIProvider, ProviderConfig, get_default_base_url

logger = logging.getLogger(__name__)


class OllamaProviderError(RuntimeError):
    pass


class OllamaLocalProvider:
    def __init__(
        self,
        base_url: str = get_default_base_url(AIProvider.OLLAMA),
        timeout_seconds: float = 60.0,
        http_client: httpx.Client | None = None,
        async_http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._client = http_client
        self._owns_client = http_client is None
        self._async_client = async_http_client
        self._owns_async_client = async_http_client is None

    def generate(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        if image_paths:
            raise OllamaProviderError(
                "Ollama's /api/generate endpoint does not support image input. "
                "Use a vision model (e.g., llava) with /api/chat or switch to a cloud provider for image analysis."
            )

        payload = {
            "model": config.model,
            "prompt": prompt,
            "stream": False,
            "system": system_prompt,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        }
        try:
            response = self._get_client(config).post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=config.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaProviderError(f"Ollama request failed for model {config.model}.") from exc

        return str(data.get("response") or "")

    async def generate_async(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        if image_paths:
            raise OllamaProviderError("Ollama /api/generate does not accept image_paths; use a vision model through /api/chat in a future provider.")

        payload = {
            "model": config.model,
            "prompt": prompt,
            "stream": False,
            "system": system_prompt,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        }
        try:
            client = await self._get_async_client(config)
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=config.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaProviderError(f"Ollama async request failed for model {config.model}.") from exc

        return str(data.get("response") or "")

    def generate_stream(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> Iterator[str]:
        if image_paths:
            raise OllamaProviderError("Ollama /api/generate does not accept image_paths; use a vision model through /api/chat in a future provider.")

        payload = {
            "model": config.model,
            "prompt": prompt,
            "stream": True,
            "system": system_prompt,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        }
        try:
            with self._get_client(config).stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=config.timeout_seconds,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.strip():
                        continue
                    event = json.loads(line)
                    chunk = event.get("response")
                    if chunk:
                        yield str(chunk)
                    if event.get("done"):
                        break
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaProviderError(f"Ollama streaming request failed for model {config.model}.") from exc

    def list_models(self) -> list[str]:
        try:
            response = self._get_client(ProviderConfig()).get(
                f"{self.base_url}/api/tags",
                timeout=10.0,
            )
            response.raise_for_status()
            models = response.json().get("models", [])
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaProviderError("Unable to list local Ollama models.") from exc

        names: list[str] = []
        for model in models:
            if isinstance(model, dict) and model.get("name"):
                names.append(str(model["name"]))
        return names

    def is_available(self) -> bool:
        try:
            response = self._get_client(ProviderConfig()).get(
                f"{self.base_url}/api/tags",
                timeout=5.0,
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
        if self._owns_async_client and self._async_client is not None:
            logger.warning("Async httpx clients should be closed by the caller.")

    def _get_client(self, config: ProviderConfig) -> httpx.Client:
        if self._client is not None:
            return self._client
        self._client = httpx.Client(timeout=config.timeout_seconds)
        self._owns_client = True
        return self._client

    async def _get_async_client(self, config: ProviderConfig) -> httpx.AsyncClient:
        if self._async_client is not None:
            return self._async_client
        self._async_client = httpx.AsyncClient(timeout=config.timeout_seconds)
        self._owns_async_client = True
        return self._async_client
