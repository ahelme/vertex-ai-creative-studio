# Provider Abstraction Architecture Draft

## Package Layout
```
providers/
  __init__.py
  registry.py          # Provider metadata, capability matrix, selector logic
  base.py              # Protocol interfaces and shared dataclasses
  google_vertex.py     # Adapters wrapping existing Google implementations
  openrouter.py        # Placeholder adapters (Phase 2)
  fal.py               # Placeholder
  replicate.py         # Placeholder
  huggingface.py       # Placeholder

models/
  provider_context.py  # (new) helpers to bridge existing workflows to providers
```

## Core Types (`providers/base.py`)
- `ProviderCapability` enum/flags (`text`, `image`, `video`, `audio`, `tts`).
- `ProviderInfo` dataclass: `name`, `display_name`, `capabilities`, `default_modality_options`, `config_keys` (env vars), `priority`, `feature_flag`.
- Interfaces (Protocols):
  - `TextModelService`
  - `ImageModelService`
  - `VideoModelService`
  - `AudioModelService`
  - `TTSService`
- Shared dataclasses:
  - `Prompt`, `MediaAttachment` (URI or inline bytes)
  - `TextGenerationResult`, `ImageGenerationResult`, etc., with `artifacts` list, metadata, `raw_response`.
  - Option objects (`TextOptions`, `ImageOptions`, ...), each with common fields and `extra: dict[str, Any]`.

## Registry (`providers/registry.py`)
- Maintains provider metadata loaded from `config/providers.yaml` (or Python map for MVP).
- Exposes:
  - `get_provider(provider_id)`
  - `list_providers(modality)` filtered by capabilities + feature flags.
  - `select_provider(modality, preference, fallback=True)` returning adapter instance + metadata.
- Handles lazy initialization of adapters; stores factory functions keyed by provider ID + modality.
- Leverages environment variables for API keys; raises descriptive errors if missing.

## Google Adapter Strategy (`providers/google_vertex.py`)
- Wrap existing functions by delegating to current modules (`models.gemini`, `models.image_models`, `models.veo`, `models.lyria`, `models.gemini_tts`).
- Provide adapter classes implementing Protocols but reusing current logic; initial version can call existing synchronous functions while we refactor internals to use service objects.
- Example skeleton:

```python
class GoogleTextService(TextModelService):
    async def generate_text(...):
        return await asyncio.to_thread(models.gemini.generate_text, ...)
```

- For image/video functions returning GCS URIs, convert into `MediaArtifact` objects.

## Workflow Integration Strategy
1. Introduce `ProviderContext` (or similar) per request to encapsulate provider selection, options.
2. Update workflow state (e.g., `state/imagen_state.py`) to carry `selected_provider` with default `"google-vertex"`.
3. Refactor UI handlers to use provider services via registry instead of calling Google modules directly.
4. Gradually migrate modules; maintain compatibility wrappers that call the provider service with `provider_id="google-vertex"` for initial release.

## Configuration & Secrets
- Environment variables (to be referenced in Terraform/Cloud Run):
  - `OPENROUTER_API_KEY`
  - `FAL_AI_API_KEY`
  - `REPLICATE_API_TOKEN`
  - `HUGGINGFACE_API_TOKEN`
- Optional: `PROVIDER_DEFAULTS_JSON` or per-workflow env var to override default provider.
- Feature flags (env) for enabling third-party providers: `ENABLE_PROVIDER_OPENROUTER`, etc.

## Observability
- Each adapter returns `ProviderTelemetry` data (latency, tokens, request ID) for logging.
- Add middleware/logging hook to emit events with provider metadata.

## Next Steps
1. Implement `providers/base.py` with Protocols and DTOs.
2. Implement `providers/registry.py` (bootstrap with Python dict config).
3. Add Google adapter classes delegating to existing functionality.
4. Update one workflow (e.g., Gemini image generation) to use registry as spike.
5. Iterate to cover remaining workflows and add third-party adapters in subsequent phases.

## Adapter Implementation Notes
- **Google Vertex AI**: Current implementation provides `GoogleImageService` and `GoogleTextService` wrappers that bridge existing Imagen and Gemini logic via the provider interfaces.  Remaining modalities (video, audio, TTS) reuse legacy code and will be ported similarly.
- **OpenRouter**: Initial `OpenRouterTextService` placeholder registered to unblock configuration work; full HTTP client integration will translate OpenRouter's OpenAI-compatible schema into the shared `TextResult` structure.
- **Adapter Pattern**: Each adapter should encapsulate provider-specific request construction, response parsing, telemetry capture, and error normalization into `ProviderError` exceptions.

## Registry Metadata Strategy
- Provider metadata (`ProviderMeta`) defines feature flags, required environment variables, default models, and priority ordering.  The registry enforces credential checks via `ensure_credentials` before adapter invocation.
- Google Vertex AI is registered by default with highest priority to preserve current behavior; third-party providers require explicit feature flags (`ENABLE_PROVIDER_*`).

## Telemetry & Logging
- Adapters populate `ProviderTelemetry` with `provider_id`, `model_name`, and latency to feed analytics instrumentation.
- UI/workflow layers should include `provider` context in existing `track_model_call` logging for comparative monitoring.
