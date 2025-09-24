# Provider Integration Research Notes

## OpenRouter
- **OpenRouterTeam/ai-sdk-provider** – Vercel AI SDK provider for OpenRouter (TypeScript) useful for understanding request schema and model catalog: https://github.com/OpenRouterTeam/ai-sdk-provider
- **BerriAI/litellm** – Polyglot Python gateway supporting OpenRouter via OpenAI-compatible schemas: https://github.com/BerriAI/litellm
- **Community Python examples** – multiple repos demonstrating OpenRouter usage (e.g., https://github.com/sriramkrish68/Easyopenchat) that highlight request headers and routing patterns.

## FAL.ai
- **fal-ai/fal** – Official Python client (pip package `fal-ai`) with async job handling (REST & websocket) (repository reference via PyPI; see docs https://www.fal.ai/docs). *(Direct GitHub metadata retrieval limited; leverage package source for detailed guidance.)*
- **cjmellor/fal-ai-laravel** – Laravel SDK illustrating REST endpoints and authentication flow: https://github.com/cjmellor/fal-ai-laravel
- **sobhanb-eth/FalAiUnitySDK** – Demonstrates job polling and asset download patterns for Fal.ai’s 3D models: https://github.com/sobhanb-eth/FalAiUnitySDK

## Replicate
- **replicate/replicate-python** – Official Python client handling job submission, polling, and output streaming: https://github.com/replicate/replicate-python
- **BerriAI/litellm** – Provides Replicate adapter in OpenAI-compatible format, useful for reuse or reference.

## Hugging Face
- **huggingface/huggingface_hub** – Official Python client for model inference, async streaming, and file handling: https://github.com/huggingface/huggingface_hub
- **huggingface/text-generation-inference** – For high-performance text generation deployments (if self-hosting is considered): https://github.com/huggingface/text-generation-inference

## Cross-Provider Aggregators / Patterns
- **microsoft/semantic-kernel** – Demonstrates multi-provider connectors with pluggable abstractions in .NET/Python: https://github.com/microsoft/semantic-kernel
- **LangChain** (https://github.com/langchain-ai/langchain) – Implements provider-agnostic wrappers (OpenRouter, Replicate, Hugging Face, etc.), helpful for interface design inspiration.
