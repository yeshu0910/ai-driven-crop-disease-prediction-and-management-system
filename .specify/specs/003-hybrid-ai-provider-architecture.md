# Feature Specification: Hybrid AI Provider Architecture

## Feature Overview
Add a production-ready AI abstraction layer that lets every generative AI feature run either locally through Ollama or through user-supplied BYOK cloud provider credentials.

## Problem Statement
Farmers and agronomists need AI assistance even when cloud connectivity is unavailable or undesirable. At the same time, users with their own provider subscriptions should be able to connect OpenAI, Anthropic, Gemini, Groq, Together AI, OpenRouter, HuggingFace, or a custom endpoint without exposing secrets in code.

## User Stories
- As a farmer, I want local Ollama inference so I can use AI features without cloud dependency.
- As a power user, I want to provide my own API key and model so I can use preferred cloud providers.
- As a developer, I want all AI features to call one provider manager so future providers can be added without duplicate logic.
- As a security reviewer, I want keys masked, validated, and stored only in session or encrypted config.

## Functional Requirements
1. Local provider routes to Ollama `http://localhost:11434/api/generate`.
2. Cloud providers route through BYOK API keys and configurable model names.
3. Provider manager exposes `generate_response(prompt, provider_config)`.
4. Model router supports local, cloud, and auto modes.
5. Cloud failures can fall back to local Ollama when enabled.
6. Responses support caching, streaming, async calls, timeout handling, and retries.
7. UI provides AI settings for provider, model, API key, base URL, temperature, max tokens, fallback, and cache.
8. Chatbot, image explanation, report summary, recommendations, translation, and summarization use the unified layer.

## Non-Functional Requirements
1. No API keys may be hardcoded or logged.
2. Keys must be masked in the UI.
3. Provider errors must not leak secrets.
4. Provider implementations must be modular and follow SOLID principles.
5. Future providers must be addable through the cloud provider registry pattern.

## Acceptance Criteria
- [ ] Local Ollama generation works through `ProviderManager`.
- [ ] Cloud provider generation works with mocked HTTP responses.
- [ ] Cloud failure falls back to local provider when enabled.
- [ ] Response cache returns cached results.
- [ ] AI settings panel stores keys in session state and masks displayed keys.
- [ ] AI assistant features call `ai.provider_manager` through shared helper functions.

## Dependencies
- `httpx`
- `cryptography`
- Streamlit session state
- Ollama local runtime for local inference

## Out of Scope
- Mobile app provider integration
- Automatic model quantization or VRAM checks
- Persistent multi-user credential vaulting
