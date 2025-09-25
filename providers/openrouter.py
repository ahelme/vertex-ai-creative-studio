"""OpenRouter provider adapter implementation."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

from providers import (
    ProviderCapability,
    ProviderError,
    ProviderMeta,
    ProviderTelemetry,
    Prompt,
    TextModelService,
    TextOptions,
    TextResult,
    registry,
)

import requests

PROVIDER_ID = "openrouter"


@dataclass
class OpenRouterConfig:
    base_url: str = "https://openrouter.ai/api/v1"
    model: str = "google/gemini-1.5-flash"
    api_key_env: str = "OPENROUTER_API_KEY"


class OpenRouterTextService(TextModelService):
    """Text generation adapter using OpenRouter's OpenAI-compatible API."""

    def __init__(self, config: OpenRouterConfig | None = None) -> None:
        self._config = config or OpenRouterConfig()

    def generate_text(
        self, prompt: Prompt, *, options: TextOptions | None = None
    ) -> TextResult:
        opts = options or TextOptions()

        api_key = os.getenv(self._config.api_key_env)
        if not api_key:
            raise ProviderError(
                "OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable."
            )

        model_name = None
        if opts.extra and isinstance(opts.extra, dict):
            model_name = opts.extra.get("model_name")
        if not model_name:
            model_name = self._config.model

        url = f"{self._config.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt.text,
                }
            ],
        }

        if opts.temperature is not None:
            payload["temperature"] = opts.temperature
        if opts.top_p is not None:
            payload["top_p"] = opts.top_p
        if opts.max_output_tokens is not None:
            payload["max_tokens"] = opts.max_output_tokens

        timeout = 30
        if opts.extra and isinstance(opts.extra, dict):
            timeout = opts.extra.get("timeout", timeout)

        start = time.perf_counter()
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        except requests.RequestException as exc:
            raise ProviderError(f"OpenRouter request failed: {exc}") from exc

        latency_ms = (time.perf_counter() - start) * 1000

        if response.status_code >= 400:
            try:
                error_json = response.json()
            except ValueError:
                error_json = response.text
            raise ProviderError(
                f"OpenRouter error {response.status_code}: {error_json}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderError("OpenRouter returned non-JSON response") from exc

        choices = data.get("choices") or []
        generations: list[str] = []
        for choice in choices:
            message = choice.get("message") or {}
            content = message.get("content")
            if content:
                generations.append(content)
        if not generations:
            raise ProviderError("OpenRouter response contained no generations")

        telemetry = ProviderTelemetry(
            provider_id=PROVIDER_ID,
            model_name=model_name,
            latency_ms=latency_ms,
            raw_info={"usage": data.get("usage")},
        )

        return TextResult(
            generations=tuple(generations),
            metadata={"model_name": model_name},
            telemetry=telemetry,
        )


def register_openrouter_provider() -> None:
    meta = ProviderMeta(
        provider_id=PROVIDER_ID,
        display_name="OpenRouter",
        capabilities=frozenset({ProviderCapability.TEXT, ProviderCapability.IMAGE}),
        env_keys={"api_key": "OPENROUTER_API_KEY"},
        feature_flag_env="ENABLE_PROVIDER_OPENROUTER",
        priority=50,
    )
    try:
        registry.register_provider(meta)
    except ValueError:
        registry.update_provider(meta)

    registry.register_adapter(
        PROVIDER_ID,
        ProviderCapability.TEXT,
        lambda: OpenRouterTextService(),
    )


register_openrouter_provider()
