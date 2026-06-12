from __future__ import annotations

import json
import logging
from collections.abc import Iterator, Mapping, Sequence
from typing import Any
from urllib.parse import quote

import httpx

from ai.settings import (
    AIProvider,
    ProviderConfig,
    coerce_provider,
    get_default_base_url,
    is_openai_compatible,
)

logger = logging.getLogger(__name__)


class CloudProviderError(RuntimeError):
    pass


class CloudProvider:
    def __init__(
        self,
        timeout_seconds: float = 60.0,
        http_client: httpx.Client | None = None,
        async_http_client: httpx.AsyncClient | None = None,
    ) -> None:
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
        provider = coerce_provider(config.provider)
        if image_paths:
            raise CloudProviderError("Image input is not supported by the current text provider interface.")

        if provider == AIProvider.ANTHROPIC:
            payload, url, headers = self._anthropic_payload(prompt, config, system_prompt)
            data = self._request_json("POST", url, headers, payload, config)
            return self._parse_anthropic_response(data)

        if provider == AIProvider.GEMINI:
            payload, url, headers = self._gemini_payload(prompt, config, system_prompt)
            data = self._request_json("POST", url, headers, payload, config)
            return self._parse_gemini_response(data)

        if provider == AIProvider.HUGGINGFACE:
            payload, url, headers = self._huggingface_payload(prompt, config, system_prompt)
            data = self._request_json("POST", url, headers, payload, config)
            return self._parse_huggingface_response(data)

        payload, url, headers = self._openai_compatible_payload(prompt, config, system_prompt)
        data = self._request_json("POST", url, headers, payload, config)
        return self._parse_openai_response(data)

    async def generate_async(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> str:
        provider = coerce_provider(config.provider)
        if image_paths:
            raise CloudProviderError("Image input is not supported by the current text provider interface.")

        if provider == AIProvider.ANTHROPIC:
            payload, url, headers = self._anthropic_payload(prompt, config, system_prompt)
            data = await self._request_json_async("POST", url, headers, payload, config)
            return self._parse_anthropic_response(data)

        if provider == AIProvider.GEMINI:
            payload, url, headers = self._gemini_payload(prompt, config, system_prompt)
            data = await self._request_json_async("POST", url, headers, payload, config)
            return self._parse_gemini_response(data)

        if provider == AIProvider.HUGGINGFACE:
            payload, url, headers = self._huggingface_payload(prompt, config, system_prompt)
            data = await self._request_json_async("POST", url, headers, payload, config)
            return self._parse_huggingface_response(data)

        payload, url, headers = self._openai_compatible_payload(prompt, config, system_prompt)
        data = await self._request_json_async("POST", url, headers, payload, config)
        return self._parse_openai_response(data)

    def generate_stream(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str = "",
        image_paths: Sequence[str] | None = None,
    ) -> Iterator[str]:
        provider = coerce_provider(config.provider)
        if image_paths:
            raise CloudProviderError("Image input is not supported by the current text provider interface.")

        if provider == AIProvider.ANTHROPIC:
            yield self.generate(prompt, config, system_prompt)
            return

        if provider == AIProvider.GEMINI:
            yield self.generate(prompt, config, system_prompt)
            return

        if provider == AIProvider.HUGGINGFACE:
            yield self.generate(prompt, config, system_prompt)
            return

        payload, url, headers = self._openai_compatible_payload(prompt, config, system_prompt, stream=True)
        try:
            with self._get_client(config).stream(
                "POST",
                url,
                headers=headers,
                json=payload,
                timeout=config.timeout_seconds,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    if line == "[DONE]":
                        break
                    event = json.loads(line)
                    delta = self._extract_openai_stream_delta(event)
                    if delta:
                        yield delta
        except (httpx.HTTPError, ValueError) as exc:
            raise CloudProviderError(f"Cloud streaming request failed for provider {provider.value}.") from exc

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
        if self._owns_async_client and self._async_client is not None:
            logger.warning("Async httpx clients should be closed by the caller.")

    def _openai_compatible_payload(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str,
        stream: bool = False,
    ) -> tuple[dict[str, object], str, dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, object] = {
            "model": config.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "stream": stream,
        }
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        return payload, self._openai_compatible_url(config), headers

    def _anthropic_payload(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str,
    ) -> tuple[dict[str, object], str, dict[str, str]]:
        payload: dict[str, object] = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        return payload, f"{self._base_url(config).rstrip('/')}/messages", headers

    def _gemini_payload(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str,
    ) -> tuple[dict[str, object], str, dict[str, str]]:
        system_text = system_prompt or "You are a precise agricultural assistant."
        payload: dict[str, object] = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_text}\n\n{prompt}"}]},
            ],
            "generationConfig": {
                "temperature": config.temperature,
                "maxOutputTokens": config.max_tokens,
            },
        }
        base_url = self._base_url(config).rstrip("/")
        url = f"{base_url}/models/{quote(config.model, safe='')}:{'generateContent'}?key={config.api_key}"
        return payload, url, {"Content-Type": "application/json"}

    def _huggingface_payload(
        self,
        prompt: str,
        config: ProviderConfig,
        system_prompt: str,
    ) -> tuple[dict[str, object], str, dict[str, str]]:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        payload: dict[str, object] = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": config.max_tokens,
                "temperature": config.temperature,
                "return_full_text": False,
            },
        }
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        base_url = self._base_url(config).rstrip("/")
        url = f"{base_url}/models/{quote(config.model, safe='')}/generate"
        return payload, url, headers

    def _request_json(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        payload: Mapping[str, object],
        config: ProviderConfig,
    ) -> dict[str, Any]:
        attempts = config.retries + 1
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                response = self._get_client(config).request(
                    method,
                    url,
                    headers=dict(headers),
                    json=dict(payload),
                    timeout=config.timeout_seconds,
                )
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict):
                    return data
                return {"raw": data}
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                if attempt >= config.retries:
                    break
        provider = coerce_provider(config.provider)
        raise CloudProviderError(f"Cloud provider request failed for {provider.value}.") from last_error

    async def _request_json_async(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        payload: Mapping[str, object],
        config: ProviderConfig,
    ) -> dict[str, Any]:
        attempts = config.retries + 1
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                client = await self._get_async_client(config)
                response = await client.request(
                    method,
                    url,
                    headers=dict(headers),
                    json=dict(payload),
                    timeout=config.timeout_seconds,
                )
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict):
                    return data
                return {"raw": data}
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                if attempt >= config.retries:
                    break
        provider = coerce_provider(config.provider)
        raise CloudProviderError(f"Cloud async provider request failed for {provider.value}.") from last_error

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

    def _base_url(self, config: ProviderConfig) -> str:
        provider = coerce_provider(config.provider)
        return config.base_url or get_default_base_url(provider)

    def _openai_compatible_url(self, config: ProviderConfig) -> str:
        provider = coerce_provider(config.provider)
        if not is_openai_compatible(provider) and provider != AIProvider.CUSTOM:
            return f"{self._base_url(config).rstrip('/')}/chat/completions"
        base_url = self._base_url(config).rstrip("/")
        if base_url.endswith("/chat/completions"):
            return base_url
        if base_url.endswith("/v1"):
            return f"{base_url}/chat/completions"
        return f"{base_url}/v1/chat/completions"

    @staticmethod
    def _parse_openai_response(data: Mapping[str, Any]) -> str:
        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise CloudProviderError("OpenAI-compatible response did not contain assistant text.") from exc

    @staticmethod
    def _parse_anthropic_response(data: Mapping[str, Any]) -> str:
        try:
            content = data["content"]
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, Mapping) and "text" in first:
                    return str(first["text"])
            return str(content)
        except (KeyError, TypeError) as exc:
            raise CloudProviderError("Anthropic response did not contain text.") from exc

    @staticmethod
    def _parse_gemini_response(data: Mapping[str, Any]) -> str:
        try:
            parts = data["candidates"][0]["content"]["parts"]
            texts = [str(part.get("text", "")) for part in parts if isinstance(part, Mapping)]
            return "".join(texts)
        except (KeyError, IndexError, TypeError) as exc:
            raise CloudProviderError("Gemini response did not contain generated text.") from exc

    @staticmethod
    def _parse_huggingface_response(data: Mapping[str, Any] | list[Any]) -> str:
        if isinstance(data, list):
            if not data:
                raise CloudProviderError("Hugging Face response was empty.")
            first = data[0]
            if isinstance(first, Mapping):
                return str(first.get("generated_text") or first.get("summary_text") or "")
            return str(first)
        return str(data.get("generated_text") or data.get("summary_text") or "")

    @staticmethod
    def _extract_openai_stream_delta(event: Mapping[str, Any]) -> str:
        try:
            choices = event["choices"]
            if not choices:
                return ""
            delta = choices[0].get("delta", {})
            return str(delta.get("content") or "")
        except (KeyError, IndexError, TypeError):
            return ""
