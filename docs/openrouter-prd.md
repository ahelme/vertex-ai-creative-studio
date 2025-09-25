# Pluggable Generation Provider PRD

## Objective
Enable Creative Studio operators to invoke multiple generation providers (Google Vertex AI, OpenRouter, Fai.ai, Replicate, Hugging Face) while preserving the existing deployment model and allowing easy future extensions.

## Problem Statement
The current application is tightly coupled to Google GenAI services (Vertex AI, GCS, Firestore) across configuration, business logic, and infrastructure. Introducing alternative providers requires invasive changes, blocking experimentation and limiting portability. We need a provider-neutral architecture that cleanly supports several third-party services alongside Google defaults.

## Success Metrics
- Users can select among Google Vertex AI, OpenRouter, Fai.ai, Replicate, and Hugging Face for supported workflows without code changes.
- Adding a new provider requires only implementing documented interfaces and configuration, targeting <2 person-days of effort.
- Google-backed flows remain fully functional with no UX regressions and latency degradation <10%.

## Target Users
- **Studio operators**: choose generation providers per workflow based on cost, capability, or compliance.
- **Developers**: extend the platform with new providers or modalities via predictable extension points.

## Scope
- Introduce provider-agnostic interfaces for each modality (text, image, video, audio, TTS).
- Deliver adapters for Google Vertex AI (existing), OpenRouter, Fai.ai, Replicate, and Hugging Face for the modalities each supports (starting with text & image; evaluate extended coverage per provider).
- Support per-workflow provider selection in application state and UI, with capability-aware defaults and feature gating.
- Allow artifacts from third-party providers to be stored via existing storage abstractions (GCS by default) while accommodating provider-hosted URLs.
- Maintain the current Google IAM/IAP deployment topology.

## Out of Scope
- Replacing Google authentication or hosting (Cloud Run, IAP).
- Building billing, quota, or analytics for third-party providers beyond usage logging.
- Migrating persistent storage away from GCS/Firestore.
- Guaranteeing full feature parity across providers for every modality at launch.

## Assumptions
- Application continues running inside GCP with outbound HTTPS access to all target providers.
- Provider coverage: OpenRouter (text/image), Fai.ai (image/video), Replicate (model marketplace covering multiple modalities), Hugging Face (text/image/audio via Inference Endpoints/APIs). Detailed capability matrix maintained as part of Phase 0.
- Secrets (API keys, tokens) are supplied through environment variables or Secret Manager integrations.
- Generated assets, regardless of origin, can be persisted in GCS buckets when necessary.

## Functional Requirements
1. Provider registry with configuration metadata (API keys, base URLs, supported capabilities, rate limits).
2. Abstract service interfaces per modality (TextModelService, ImageModelService, VideoModelService, AudioModelService, TTSService) with clear method contracts.
3. Google implementations refactored to conform to the interfaces without changing behavior.
4. Adapters for OpenRouter, Fai.ai, Replicate, and Hugging Face implementing interfaces for their supported modalities.
5. UI/state management capturing provider selection, surfacing only compatible options, and routing requests accordingly.
6. Error handling surfacing provider-specific failures with meaningful messaging and remediation hints.

## Non-Functional Requirements
- Abstraction layer introduces negligible latency (<10% overhead versus direct calls).
- Logging/metrics include provider identifiers for observability and basic usage analytics.
- Secrets handled securely (no plaintext commits; use Secret Manager or Cloud Run env vars).
- Automated tests validate provider selection logic, capability filtering, and adapter behaviors with mocked responses.
- System tolerates provider outages via configurable fallbacks or user notifications.

## Dependencies
- API access and credentials for OpenRouter, Fai.ai, Replicate, and Hugging Face.
- HTTP client library (httpx) with retry logic and sensible timeouts per provider SLAs.
- Potential Mesop UI updates to render provider selectors and capability tooltips.

## Risks & Mitigations
- **Capability mismatches**: maintain capability matrix and disable unsupported UI actions per provider.
- **Latency/quotas**: implement timeouts/backoff and surface rate-limit messaging; allow fallback provider selection.
- **Security/compliance**: verify outbound requests conform to policy; document data handling for each provider.
- **CSP or egress restrictions**: confirm Cloud Run configuration permits outbound HTTPS to provider domains.

## Open Questions
- Should provider access be governed per user/role? (policy decision pending).
- Can artifacts stay on provider-hosted URLs, or must they always be copied into GCS? (ops decision).
- How will cost tracking or chargeback differ per provider? (finance alignment needed).

## Release Considerations
- Feature flag to enable non-Google providers in controlled environments.
- Documentation updates (README, developer guide) covering configuration, secrets, capability matrix, and troubleshooting.
- Operator training on provider selection, capability differences, and interpreting observability signals.
