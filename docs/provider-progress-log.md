# Provider Integration Progress Log

## 2025-09-22
- Established provider abstraction layer (`providers` package) with registry, shared DTOs, and Google Vertex image/text adapters.
- Updated Imagen UI to allow provider selection and route all calls through the registry.
- Added configuration docs covering environment variables, feature flags, and adapter architecture.

## 2025-09-23
- Implemented Google Vertex TTS adapter and registered it alongside existing image/text services.
- Added initial OpenRouter text adapter implementation leveraging the OpenAI-compatible `/chat/completions` endpoint.
- Documented outstanding work items in `plans/provider-issues.md` and tracked issue status updates.
