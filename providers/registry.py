"""Provider registry and selection logic."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from .base import ProviderCapability


@dataclass(slots=True)
class ProviderMeta:
    """Metadata describing a provider's capabilities and configuration."""

    provider_id: str
    display_name: str
    capabilities: frozenset[ProviderCapability]
    env_keys: dict[str, str] = field(default_factory=dict)
    feature_flag_env: str | None = None
    priority: int = 100
    default_models: dict[str, str] = field(default_factory=dict)

    def is_enabled(self) -> bool:
        """Returns True when the provider is enabled via feature flag or unconditionally."""
        if not self.feature_flag_env:
            return True
        value = os.getenv(self.feature_flag_env, "false").lower()
        return value in {"1", "true", "yes", "on"}

    def requires_credentials(self) -> bool:
        return bool(self.env_keys)


class ProviderRegistry:
    """Holds provider definitions and adapter factories."""

    def __init__(self) -> None:
        self._providers: dict[str, ProviderMeta] = {}
        self._factories: dict[tuple[str, ProviderCapability], Callable[[], Any]] = {}

    def register_provider(self, meta: ProviderMeta) -> None:
        if meta.provider_id in self._providers:
            raise ValueError(f"Provider '{meta.provider_id}' already registered")
        self._providers[meta.provider_id] = meta

    def update_provider(self, meta: ProviderMeta) -> None:
        self._providers[meta.provider_id] = meta

    def get_provider(self, provider_id: str) -> ProviderMeta:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise KeyError(f"Unknown provider '{provider_id}'") from exc

    def register_adapter(
        self,
        provider_id: str,
        capability: ProviderCapability,
        factory: Callable[[], Any],
    ) -> None:
        if provider_id not in self._providers:
            raise ValueError(f"Register provider metadata before adding adapters: '{provider_id}'")
        self._factories[(provider_id, capability)] = factory

    def list_providers(
        self,
        capability: ProviderCapability | None = None,
        *,
        include_disabled: bool = False,
    ) -> list[ProviderMeta]:
        providers: Iterable[ProviderMeta]
        providers = self._providers.values()
        results: list[ProviderMeta] = []
        for meta in providers:
            if capability and capability not in meta.capabilities:
                continue
            if not include_disabled and not meta.is_enabled():
                continue
            results.append(meta)
        results.sort(key=lambda m: (m.priority, m.display_name.lower()))
        return results

    def get_adapter(self, provider_id: str, capability: ProviderCapability) -> Any:
        try:
            factory = self._factories[(provider_id, capability)]
        except KeyError as exc:
            raise KeyError(
                f"No adapter registered for provider '{provider_id}' capability '{capability.value}'"
            ) from exc
        return factory()

    def ensure_credentials(self, provider_id: str) -> None:
        meta = self.get_provider(provider_id)
        missing: list[str] = []
        for env_name in meta.env_keys.values():
            if not os.getenv(env_name):
                missing.append(env_name)
        if missing:
            joined = ", ".join(sorted(set(missing)))
            raise RuntimeError(
                f"Provider '{provider_id}' requires environment variables: {joined}"
            )


registry = ProviderRegistry()
"""Global provider registry instance used by the application."""
