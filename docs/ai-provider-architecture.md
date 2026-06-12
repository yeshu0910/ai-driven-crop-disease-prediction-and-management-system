# AI Provider Architecture

The application now uses a single AI abstraction layer for every generative AI feature:

```text
crop_disease_ai/ai/
├── provider_manager.py
├── local_provider.py
├── cloud_provider.py
├── model_router.py
└── settings.py
```

## Routing behavior

- `provider=ollama` or `mode=local` routes to `http://localhost:11434/api/generate`.
- `mode=cloud` routes to the selected BYOK provider using the user-supplied API key.
- `mode=auto` uses cloud when an API key is present, otherwise local Ollama.
- Cloud failures fall back to local Ollama when `enable_local_fallback=true`.

## Supported providers

Local:

- Ollama models such as `llama3`, `mistral`, `phi3`, `gemma`, and `codellama`.

Cloud / BYOK:

- OpenAI
- Anthropic
- Google Gemini
- Groq
- Together AI
- OpenRouter
- HuggingFace Inference API
- Custom OpenAI-compatible endpoint

## Core API

```python
from ai.provider_manager import ProviderManager, generate_response
from ai.settings import ProviderConfig

response = generate_response(
    "Explain this crop disease diagnosis.",
    ProviderConfig(provider="ollama", mode="local", model="llama3"),
)
print(response.text)
```

Streaming:

```python
from ai.provider_manager import generate_stream

for chunk in generate_stream(
    "Write a treatment checklist for tomato early blight.",
    ProviderConfig(provider="openai", mode="cloud", model="gpt-4o-mini", api_key="sk-..."),
):
    print(chunk.text, end="", flush=True)
```

Async:

```python
response = await ProviderManager().generate_response_async(
    "Summarize these recommendations.",
    ProviderConfig(provider="ollama", mode="local", model="mistral"),
)
```

## Example API requests

Local Ollama:

```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3","prompt":"List tomato disease symptoms.","stream":false}'
```

OpenAI-compatible:

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Explain crop disease severity."}],"temperature":0.2,"max_tokens":512}'
```

Anthropic:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-5-haiku-latest","max_tokens":512,"messages":[{"role":"user","content":"Summarize treatment guidance."}]}'
```

Gemini:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"role":"user","parts":[{"text":"Translate guidance to Hindi."}]}]}'
```

## Security rules

- API keys are never hardcoded.
- UI keys are stored in Streamlit session state only.
- Keys can be saved locally only through encrypted config backup.
- UI masks stored keys with `mask_api_key()`.
- Provider errors do not include API key values.
- All generative AI calls go through `ai.provider_manager`.

## Setup

```bash
ollama serve
ollama pull llama3
ollama pull mistral
```

Run the Streamlit app:

```bash
streamlit run crop_disease_ai/app.py
```

Optional environment defaults:

```bash
AI_PROVIDER=ollama
AI_PROVIDER_MODE=local
AI_MODEL=llama3
AI_BASE_URL=http://localhost:11434
AI_ENABLE_LOCAL_FALLBACK=true
```

For BYOK, select a cloud provider in the AI Settings sidebar and enter your own key, model, optional base URL, temperature, and max tokens.
