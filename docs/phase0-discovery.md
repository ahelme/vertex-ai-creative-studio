# Phase 0 Discovery Summary

## Workflow Inventory & Current Dependencies

| Workflow / Feature | Modality | Entry Points | Google-Specific Dependencies |
| --- | --- | --- | --- |
| Gemini Image Generation (`pages/gemini_image_generation.py`) | Image + Text-to-image | `models/gemini.generate_image_from_prompt_and_images`, `models/model_setup.GeminiModelSetup` | `google.genai`, Vertex AI initialization, GCS storage (`common/storage.py`), Firestore session logging |
| Imagen Creative Studio (`pages/imagen.py`) | Image generation | `models/image_models.generate_images` | `google.genai`, Vertex AI, GCS output URIs |
| Character Consistency (`pages/character_consistency.py`) | Text + Image | `models/character_consistency.py` | `google.genai`, Vertex AI, GCS |
| Shop the Look (`pages/shop_the_look.py`) | Image search/generation | `models/shop_the_look_workflow.py`, `models/gemini.py` | `google.genai`, Vertex AI, Firestore |
| Veo Video Generation (`pages/veo`) | Video | `models/veo.generate_video`, `models/model_setup.VeoModelSetup` | `google.genai`, Vertex AI video models, GCS buckets |
| Virtual Try-On (`models/vto.py`, `models/model_setup.VtoModelSetup`) | Image/Video | Vertex AI prediction service | `vertexai`, `google.cloud.aiplatform` |
| Lyria Music Generation (`pages/lyria.py`) | Audio (music) | `models/lyria.generate_music_with_lyria` | `vertexai`, `google.cloud.aiplatform`, GCS |
| Gemini Text-to-Speech (`pages/gemini_tts.py`) | TTS | `models/gemini_tts.synthesize_speech` | `google.cloud.texttospeech` |
| Interior Design, Starter Pack, other text workflows | Text + Image | `models/gemini`, `models/image_models` | `google.genai`, Vertex AI |
| Asset storage, session tracking | Cross-cutting | `common/storage.store_to_gcs`, `config/firebase_config.FirebaseClient` | Google Cloud Storage, Firestore, IAM impersonation |
| Front-end hosting & Auth | Cross-cutting | `main.py`, Terraform | Cloud Run, IAP, Google auth headers |

## Provider Capability Matrix (Initial Pass)

| Provider | Text (LLM) | Image Gen | Video Gen | Audio/Music | TTS | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Google Vertex AI (existing) | ✅ Gemini models | ✅ Imagen | ✅ Veo | ✅ Lyria | ✅ Gemini TTS | Current default, tight integration |
| OpenRouter | ✅ (chat/completions proxy to many LLMs) | ⚠️ limited (some partner models expose image endpoints) | ❌ | ⚠️ limited (some hosted audio models) | ❌ | Aggregates non-Google APIs behind OpenAI-compatible schema |
| FAL.ai | ⚠️ (some hosted text endpoints) | ✅ (Flux, SDXL variants) | ✅ (video models like Kling, Haiper) | ⚠️ (audio tools) | ❌ | REST/async jobs; responses via webhooks/polling |
| Replicate | ✅ (via community models) | ✅ | ✅ | ✅ | ⚠️ (depends on model) | Job-based API with webhooks, strong Python client |
| Hugging Face (Inference API) | ✅ | ✅ | ⚠️ (limited via specific models) | ✅ | ✅ (Text-to-Speech models) | Supports both hosted inference endpoints and serverless pipelines |

Legend: ✅ = native/first-class support, ⚠️ = available via selected models or needs custom handling, ❌ = not available/unsupported.

## Proposed Service Interfaces (Draft)

```python
class TextModelService(Protocol):
    async def generate_text(self, prompt: Prompt, *, options: TextOptions) -> TextGenerationResult: ...

class ImageModelService(Protocol):
    async def generate_images(self, prompt: Prompt, *, options: ImageOptions) -> ImageGenerationResult: ...

class VideoModelService(Protocol):
    async def generate_video(self, prompt: Prompt, *, options: VideoOptions) -> VideoGenerationResult: ...

class AudioModelService(Protocol):
    async def generate_audio(self, prompt: Prompt, *, options: AudioOptions) -> AudioGenerationResult: ...

class TTSService(Protocol):
    async def synthesize(self, text: str, *, voice: VoiceConfig, options: TTSOptions) -> TTSResult: ...
```

Shared DTOs (subject to refinement):

```python
@dataclass
class Prompt:
    text: str
    media: list[MediaAttachment] = field(default_factory=list)

@dataclass
class MediaAttachment:
    type: Literal["image", "audio", "video"]
    uri: str | None = None
    data: bytes | None = None
    mime_type: str | None = None
```

Each `*Options` object encapsulates provider-agnostic parameters (e.g., `temperature`, `aspect_ratio`, `negative_prompt`) plus `extra: dict[str, Any]` for provider-specific overrides.

## Configuration & Registry Strategy

- Provider registry: YAML/JSON or Python config enumerating providers, supported modalities, base URLs, priority, and environment-variable names for credentials.
- Capabilities attached to registry entries to guide UI filtering and fallback logic.
- Secrets managed via Cloud Run environment variables pointing to Secret Manager (`OPENROUTER_API_KEY`, `FALAI_API_KEY`, `REPLICATE_API_TOKEN`, `HF_API_TOKEN`).
- Per-workflow configuration maps default provider and allowed providers (with feature flags).

## Architecture Overview (Target)

```
[Mesop UI] ──▶ [Workflow Controller] ──▶ [ProviderSelector]
                                   │
                                   ├──▶ [TextModelService | ImageModelService | ...]
                                   │        ├── VertexAIAdapter
                                   │        ├── OpenRouterAdapter
                                   │        ├── FALAdapter
                                   │        ├── ReplicateAdapter
                                   │        └── HuggingFaceAdapter
                                   └──▶ [Storage Orchestrator] ──▶ GCS / External URLs
```

- ProviderSelector uses capability matrix to pick an adapter (default or user-selected) and handles fallback.
- Storage Orchestrator normalizes outputs into `MediaArtifact` objects (with metadata, URIs, temp storage) before persisting.
- Observability layer emits structured logs (`provider`, `modality`, `latency_ms`, `status`).

## Outstanding Questions from Phase 0

1. Do we normalize all outputs into GCS blobs, or allow referencing provider-hosted URLs when permitted?
2. What are acceptable latency budgets per workflow when backing providers rely on asynchronous job polling (e.g., Replicate, FAL.ai video)?
3. Should provider selection be per-session, per-user, or per-request? (Impacts state management.)
4. Are there compliance constraints for routing user-provided assets to third-party clouds?

## Recommended Next Actions

- Validate capability matrix and data-handling rules with product/security stakeholders.
- Finalize interface method signatures (sync vs async, streaming support) based on workflow needs.
- Draft configuration schema (likely JSONSchema or Pydantic model) for provider registry.
- Prepare Secret Manager entries and reference them in deployment manifests (Terraform/Cloud Run).
