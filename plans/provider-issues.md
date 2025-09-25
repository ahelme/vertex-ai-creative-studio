# Provider Integration Issue Tracker

## Issue 1: Implement Google Vertex TTS Adapter
- **Status:** Completed 2025-09-23
- **Summary:** Wrap existing Gemini TTS logic inside provider interface (`GoogleTTSService`) and register under `ProviderCapability.TTS`.
- **Notes:** Adapter leverages `models.gemini_tts.synthesize_speech` and returns audio artifacts via `MediaArtifact`.

## Issue 2: Implement OpenRouter Text Adapter
- **Status:** Completed 2025-09-23
- **Summary:** Added HTTP client integration against OpenRouter's `chat/completions` endpoint with telemetry + error handling, controlled via `OPENROUTER_API_KEY` feature flag.

## Issue 3: Update Terraform/Env Templates for Provider Secrets
- **Status:** Pending
- **Summary:** Propagate new provider env vars/flags into infrastructure templates (`main.tf`, `.env`).

## Issue 4: Extend Provider Coverage (Video/Audio) for Google & Third Parties
- **Status:** Pending
- **Summary:** Implement adapters for Veo, Lyria, FAL.ai, Replicate, and Hugging Face; update workflows incrementally.
