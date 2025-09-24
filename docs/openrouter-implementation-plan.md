# Multi-Provider Integration Implementation Plan

## Phase 0 – Discovery & Architecture (≈1 sprint)
- Inventory all workflows by modality and document existing Google dependencies and touchpoints.
- Build provider capability matrix covering Google Vertex AI, OpenRouter, Fai.ai, Replicate, and Hugging Face (modalities, rate limits, auth, response formats).
- Define modality-specific service interfaces and shared data contracts (prompts, media assets, metadata schemas).
- Document configuration strategy (env vars, Secret Manager) and networking considerations for outbound access.
- Produce architectural diagram showing provider registry, adapters, capability gating, and data flow.

## Phase 1 – Core Abstraction Layer (≈1 sprint)
- Implement provider registry/config models (env-driven metadata, capability flags, priority/fallback rules).
- Introduce interface definitions: `TextModelService`, `ImageModelService`, `VideoModelService`, `AudioModelService`, `TTSService`, plus shared DTOs.
- Wrap existing Google implementations behind interfaces with no behavioral changes; add capability descriptors.
- Update business logic modules (e.g., `models/gemini.py`, `models/image_models.py`, `models/veo.py`, `models/lyria.py`) to call through interfaces.
- Add unit tests for registry, interface contracts, and Google adapters using mocks.

## Phase 2 – Third-Party Adapters MVP (≈1.5 sprints)
- Implement OpenRouter and Hugging Face adapters for text/image modalities (HTTP clients, request/response normalization, safety filtering translation).
- Integrate capability matrix to surface only valid provider options per workflow; add feature flags per provider.
- Extend storage pipeline to ingest external responses (bytes, URLs) and persist to GCS where required.
- Update relevant UI pages with provider selector controls, capability tooltips, and state wiring.
- Create integration tests with mocked provider endpoints; ensure consistent error messaging.

## Phase 3 – Additional Providers & Modalities (≈1 sprint)
- Implement Fai.ai and Replicate adapters for supported modalities (initially image/video, extend as needed).
- Expand adapters to cover audio/video/TTS where providers support them; update workflows incrementally.
- Enhance capability matrix and UI to reflect modality-specific availability and constraints.
- Add contract tests to verify adapters conform to service interface expectations.

## Phase 4 – UX, Observability & Resilience (≈0.5 sprint)
- Refine provider selection UX (defaults, tooltips, warnings on rate limits or missing capabilities).
- Instrument logging/metrics: provider tags, latency histograms, error codes, fallback events.
- Implement fallback strategies (e.g., auto-switch to default provider on outage) configurable per workflow.
- Update documentation (README, developer/deployment guides) with setup instructions, capability tables, troubleshooting tips.

## Phase 5 – Hardening & Release (≈0.5 sprint)
- Run regression and load tests across all provider flows; validate latency targets.
- Verify Cloud Run/IAP deployment with new environment variables and secret references for all providers.
- Finalize rollout checklist, enable feature flags in staging, gather feedback, and plan production launch.

## Immediate Next Steps
1. Review updated PRD/plan with stakeholders; confirm provider scope, storage expectations, and policy requirements.
2. Acquire API credentials for OpenRouter, Fai.ai, Replicate, and Hugging Face; set up Secret Manager entries.
3. Execute Phase 0 tasks: dependency inventory, capability matrix, interface specification, and architecture documentation.
