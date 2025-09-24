"""Google Vertex AI provider adapters and registration."""

from __future__ import annotations

import time
from typing import Any

from config.default import Default
from config.gemini_tts import GEMINI_TTS_MODEL_NAMES

from google.genai import types as genai_types

from models import gemini as gemini_models
from models import gemini_tts
from models import image_models

from . import registry
from .base import (
    ImageModelService,
    ImageOptions,
    ImageResult,
    MediaArtifact,
    Prompt,
    ProviderCapability,
    ProviderMeta,
    ProviderTelemetry,
    TTSOptions,
    TTSResult,
    TTSService,
    TextModelService,
    TextOptions,
    TextResult,
)

PROVIDER_ID = "google-vertex"


def register_google_provider() -> ProviderMeta:
    """Register Google Vertex provider metadata and placeholder adapters."""
    meta = ProviderMeta(
        provider_id=PROVIDER_ID,
        display_name="Google Vertex AI",
        capabilities=frozenset(
            {
                ProviderCapability.TEXT,
                ProviderCapability.IMAGE,
                ProviderCapability.VIDEO,
                ProviderCapability.AUDIO,
                ProviderCapability.TTS,
            }
        ),
        priority=10,
    )
    try:
        registry.register_provider(meta)
    except ValueError:
        registry.update_provider(meta)

    def _not_implemented_factory(capability: ProviderCapability) -> Any:
        def _factory() -> Any:
            raise NotImplementedError(
                f"Google provider adapter for capability '{capability.value}' not yet implemented"
            )

        return _factory

    for capability in meta.capabilities:
        registry.register_adapter(PROVIDER_ID, capability, _not_implemented_factory(capability))

    return meta


class GoogleImageService(ImageModelService):
    """Adapter that delegates image generation to existing Google Imagen logic."""

    def __init__(self) -> None:
        self._config = Default()

    def generate_images(
        self, prompt: Prompt, *, options: ImageOptions | None = None
    ) -> ImageResult:
        opts = options or ImageOptions()
        model_name = (
            opts.extra.get("model_name")
            if opts.extra and isinstance(opts.extra, dict)
            else None
        )
        if not model_name:
            model_name = self._config.MODEL_IMAGEN4

        aspect_ratio = opts.aspect_ratio or "1:1"
        negative_prompt = opts.negative_prompt or ""
        image_count = max(1, opts.count or 1)
        start = time.perf_counter()
        response = image_models.generate_images(
            model=model_name,
            prompt=prompt.text,
            number_of_images=image_count,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        artifacts: list[MediaArtifact] = []
        candidates = getattr(response, "generated_images", []) or []
        for index, candidate in enumerate(candidates):
            image_obj = getattr(candidate, "image", None)
            uri = getattr(image_obj, "gcs_uri", None)
            mime_type = getattr(image_obj, "mime_type", None)
            artifacts.append(
                MediaArtifact(
                    kind="image",
                    uri=uri,
                    mime_type=mime_type,
                    metadata={
                        "candidate_index": index,
                    },
                )
            )

        metadata = {
            "model_name": model_name,
            "candidate_count": len(artifacts),
        }

        telemetry = ProviderTelemetry(
            provider_id=PROVIDER_ID,
            model_name=model_name,
            latency_ms=latency_ms,
        )

        return ImageResult(
            artifacts=tuple(artifacts),
            metadata=metadata,
            telemetry=telemetry,
        )


class GoogleTextService(TextModelService):
    """Adapter that delegates text generation to existing Gemini logic."""

    def __init__(self) -> None:
        self._config = Default()

    def generate_text(
        self, prompt: Prompt, *, options: TextOptions | None = None
    ) -> TextResult:
        opts = options or TextOptions()
        model_name = None
        if opts.extra and isinstance(opts.extra, dict):
            model_name = opts.extra.get("model_name")
        if not model_name or model_name not in GEMINI_TTS_MODEL_NAMES:
            model_name = GEMINI_TTS_MODEL_NAMES[0]

        contents = [prompt.text]
        config = genai_types.GenerateContentConfig(
            response_modalities=["TEXT"],
            temperature=opts.temperature,
            top_p=opts.top_p,
            max_output_tokens=opts.max_output_tokens,
            safety_settings=opts.safety_settings,
        )
        response = gemini_models.client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )

        generations: list[str] = []
        if getattr(response, "text", None):
            generations.append(response.text)
        elif response.candidates:
            for candidate in response.candidates:
                parts = getattr(candidate, "content", None)
                if parts and getattr(parts, "parts", None):
                    for part in parts.parts:
                        text_value = getattr(part, "text", None)
                        if text_value:
                            generations.append(text_value)

        telemetry = ProviderTelemetry(
            provider_id=PROVIDER_ID,
            model_name=model_name,
        )

        return TextResult(
            generations=tuple(generations),
            metadata={"model_name": model_name},
            telemetry=telemetry,
        )


class GoogleTTSService(TTSService):
    """Adapter that delegates TTS to Gemini Text-to-Speech."""

    def __init__(self) -> None:
        self._config = Default()

    def synthesize(
        self, text: str, *, options: TTSOptions | None = None
    ) -> TTSResult:
        opts = options or TTSOptions()
        model_name = (
            opts.extra.get("model_name")
            if opts.extra and isinstance(opts.extra, dict)
            else self._config.MODEL_ID
        )
        voice_name = opts.voice or "Alnilam"
        language_code = opts.language_code or "en-US"
        prompt_text = opts.extra.get("prompt", "") if opts.extra else ""

        audio_bytes = gemini_tts.synthesize_speech(
            text=text,
            prompt=prompt_text,
            model_name=model_name,
            voice_name=voice_name,
            language_code=language_code,
        )

        artifact = MediaArtifact(
            kind="audio",
            data=audio_bytes,
            mime_type="audio/wav",
            metadata={
                "voice_name": voice_name,
                "language_code": language_code,
            },
        )

        telemetry = ProviderTelemetry(
            provider_id=PROVIDER_ID,
            model_name=model_name,
        )

        return TTSResult(
            audio=artifact,
            metadata={"model_name": model_name},
            telemetry=telemetry,
        )


# Perform registration on import and override implemented adapters.
_META = register_google_provider()

registry.register_adapter(
    PROVIDER_ID,
    ProviderCapability.IMAGE,
    lambda: GoogleImageService(),
)

registry.register_adapter(
    PROVIDER_ID,
    ProviderCapability.TEXT,
    lambda: GoogleTextService(),
)

registry.register_adapter(
    PROVIDER_ID,
    ProviderCapability.TTS,
    lambda: GoogleTTSService(),
)
