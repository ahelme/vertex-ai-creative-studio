# Multi-Provider Configuration & Secrets

## Environment Variables
Set the following environment variables (ideally sourced from Secret Manager and injected into Cloud Run):

| Variable | Purpose | Applies To |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | Bearer token for OpenRouter requests (sent via `Authorization: Bearer`). | OpenRouter adapters |
| `FAL_AI_API_KEY` | API key for FAL.ai REST / task endpoints. | FAL adapters |
| `REPLICATE_API_TOKEN` | Access token for Replicate job API. | Replicate adapters |
| `HUGGINGFACE_API_TOKEN` | Personal access token for Hugging Face Inference API. | Hugging Face adapters |
| `ENABLE_PROVIDER_OPENROUTER` | Optional feature flag (`true`/`false`) to expose OpenRouter in UI. | Registry feature gating |
| `ENABLE_PROVIDER_FAL_AI` | Optional feature flag for FAL.ai. | Registry feature gating |
| `ENABLE_PROVIDER_REPLICATE` | Optional feature flag for Replicate. | Registry feature gating |
| `ENABLE_PROVIDER_HUGGINGFACE` | Optional feature flag for Hugging Face. | Registry feature gating |
| `PROVIDER_DEFAULTS_JSON` | JSON override specifying default provider per workflow (e.g., `{ "imagen": "google-vertex" }`). | Provider selector |

## Secret Management Workflow
1. Store provider tokens in Google Secret Manager (`openrouter-api-key`, `fal-ai-api-key`, etc.).
2. Update Terraform / Cloud Run deployment to mount these secrets as environment variables (use `google_cloud_run_v2_service` secret env). 
3. For local development, extend `.env` (via `dotenv.template`) with placeholder keys and instructions.

### Terraform Snippet (Conceptual)
```hcl
dynamic "env" {
  for_each = {
    OPENROUTER_API_KEY = "openrouter-api-key"
    FAL_AI_API_KEY     = "fal-ai-api-key"
    REPLICATE_API_TOKEN = "replicate-api-token"
    HUGGINGFACE_API_TOKEN = "huggingface-api-token"
  }
  content {
    name = env.key
    value_source {
      secret_key_ref {
        secret  = env.value
        version = "latest"
      }
    }
  }
}
```

## Provider Registry Defaults
- Metadata seeded in `providers/registry.py` (or future `config/providers.yaml`) should map provider IDs to environment variable names to allow automated validation (`registry.ensure_credentials`).
- Example metadata entry:

```python
registry.register_provider(
    ProviderMeta(
        provider_id="openrouter",
        display_name="OpenRouter",
        capabilities=frozenset({ProviderCapability.TEXT, ProviderCapability.IMAGE}),
        env_keys={"api_key": "OPENROUTER_API_KEY"},
        feature_flag_env="ENABLE_PROVIDER_OPENROUTER",
        priority=50,
    )
)
```

## Logging & Monitoring
- Emit structured logs with provider ID, capability, model name, and status to simplify incident response.
- Consider separate log-based metrics per provider to monitor quota usage and error rates.

## Operational Considerations
- Rate Limiting: incorporate adaptive retry/backoff respecting provider-specific headers (`Retry-After`, `X-RateLimit-*`).
- Data Residency: confirm compliance requirements before enabling providers in specific regions; maintain allowlist configuration.
- Audit: track provider selection per user/session for auditing and cost attribution (persist in Firestore collection if needed).

## Provider Feature Flags
Enable providers per environment by setting the corresponding feature flag environment variables:

| Provider | Feature Flag | Default |
| --- | --- | --- |
| Google Vertex AI | *(n/a – always enabled)* | Enabled |
| OpenRouter | `ENABLE_PROVIDER_OPENROUTER` | Disabled |
| FAL.ai | `ENABLE_PROVIDER_FAL_AI` | Disabled |
| Replicate | `ENABLE_PROVIDER_REPLICATE` | Disabled |
| Hugging Face | `ENABLE_PROVIDER_HUGGINGFACE` | Disabled |

Set flag values to `true`, `1`, or `on` to enable.  The provider registry filters disabled providers from UI picker options.
