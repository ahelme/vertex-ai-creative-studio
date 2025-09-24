"""Provider interfaces and registry for multi-provider generation services."""

from .base import (
    AudioModelService,
    AudioOptions,
    AudioResult,
    ImageModelService,
    ImageOptions,
    ImageResult,
    MediaArtifact,
    MediaAttachment,
    Prompt,
    ProviderCapability,
    ProviderError,
    ProviderTelemetry,
    TextModelService,
    TextOptions,
    TextResult,
    TTSOptions,
    TTSResult,
    TTSService,
    VideoModelService,
    VideoOptions,
    VideoResult,
)
from .registry import ProviderMeta, ProviderRegistry, registry

# Ensure built-in providers register themselves on package import.
from . import google_vertex  # noqa: F401  pylint: disable=unused-import
from . import openrouter  # noqa: F401  pylint: disable=unused-import

__all__ = [
    "AudioModelService",
    "AudioOptions",
    "AudioResult",
    "ImageModelService",
    "ImageOptions",
    "ImageResult",
    "MediaArtifact",
    "MediaAttachment",
    "Prompt",
    "ProviderCapability",
    "ProviderError",
    "ProviderMeta",
    "ProviderRegistry",
    "ProviderTelemetry",
    "TextModelService",
    "TextOptions",
    "TextResult",
    "TTSOptions",
    "TTSResult",
    "TTSService",
    "VideoModelService",
    "VideoOptions",
    "VideoResult",
    "registry",
]
