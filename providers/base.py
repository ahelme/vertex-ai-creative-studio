"""Core provider interfaces, data contracts, and shared models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, MutableMapping, Protocol, Sequence, runtime_checkable


class ProviderCapability(str, Enum):
    """Modalities supported by generation providers."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TTS = "tts"


@dataclass
class MediaAttachment:
    """Represents an input media attachment supplied alongside a prompt."""

    kind: str
    uri: str | None = None
    data: bytes | None = None
    mime_type: str | None = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)


@dataclass
class Prompt:
    """Container for user prompt text and optional media attachments."""

    text: str
    attachments: Sequence[MediaAttachment] = field(default_factory=tuple)


@dataclass
class MediaArtifact:
    """Represents a generated media output artifact."""

    kind: str
    uri: str | None = None
    data: bytes | None = None
    mime_type: str | None = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)


@dataclass
class ProviderTelemetry:
    """Telemetry information emitted by a provider call."""

    provider_id: str
    model_name: str | None = None
    latency_ms: float | None = None
    request_id: str | None = None
    token_usage: Mapping[str, int] | None = None
    raw_info: Mapping[str, Any] | None = None


class ProviderError(RuntimeError):
    """Raised when a provider encounters a recoverable error."""


@dataclass
class BaseOptions:
    """Common option bag for provider invocations."""

    extra: MutableMapping[str, Any] = field(default_factory=dict)


@dataclass
class TextOptions(BaseOptions):
    temperature: float | None = None
    top_p: float | None = None
    max_output_tokens: int | None = None
    safety_settings: Mapping[str, Any] | None = None


@dataclass
class ImageOptions(BaseOptions):
    aspect_ratio: str | None = None
    negative_prompt: str | None = None
    count: int = 1
    seed: int | None = None


@dataclass
class VideoOptions(BaseOptions):
    aspect_ratio: str | None = None
    duration_seconds: int | None = None
    resolution: str | None = None
    frame_rate: int | None = None
    audio_enabled: bool | None = None


@dataclass
class AudioOptions(BaseOptions):
    duration_seconds: int | None = None
    voice: str | None = None


@dataclass
class TTSOptions(BaseOptions):
    voice: str | None = None
    language_code: str | None = None
    speaking_rate: float | None = None


@dataclass
class TextResult:
    """Represents the response from a text generation request."""

    generations: Sequence[str]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    telemetry: ProviderTelemetry | None = None


@dataclass
class ImageResult:
    """Represents the response from an image generation request."""

    artifacts: Sequence[MediaArtifact]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    telemetry: ProviderTelemetry | None = None


@dataclass
class VideoResult:
    """Represents the response from a video generation request."""

    artifacts: Sequence[MediaArtifact]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    telemetry: ProviderTelemetry | None = None


@dataclass
class AudioResult:
    """Represents the response from an audio generation request."""

    artifacts: Sequence[MediaArtifact]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    telemetry: ProviderTelemetry | None = None


@dataclass
class TTSResult:
    """Represents the response from a TTS synthesis request."""

    audio: MediaArtifact
    metadata: Mapping[str, Any] = field(default_factory=dict)
    telemetry: ProviderTelemetry | None = None


@runtime_checkable
class TextModelService(Protocol):
    """Interface for provider-backed text generation."""

    def generate_text(self, prompt: Prompt, *, options: TextOptions | None = None) -> TextResult: ...


@runtime_checkable
class ImageModelService(Protocol):
    """Interface for provider-backed image generation."""

    def generate_images(self, prompt: Prompt, *, options: ImageOptions | None = None) -> ImageResult: ...


@runtime_checkable
class VideoModelService(Protocol):
    """Interface for provider-backed video generation."""

    def generate_video(self, prompt: Prompt, *, options: VideoOptions | None = None) -> VideoResult: ...


@runtime_checkable
class AudioModelService(Protocol):
    """Interface for provider-backed audio generation."""

    def generate_audio(self, prompt: Prompt, *, options: AudioOptions | None = None) -> AudioResult: ...


@runtime_checkable
class TTSService(Protocol):
    """Interface for provider-backed speech synthesis."""

    def synthesize(self, text: str, *, options: TTSOptions | None = None) -> TTSResult: ...
