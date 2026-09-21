# Pluggable LLM Backends

The graph does not directly construct a provider client.

Instead:

```text
Graph node
   ↓
LLM factory
   ↓
provider adapter
```

Supported adapters:

```text
mock
ollama
openrouter
gemini
openai
```

## Mock

Used for tests.

No network and no credentials.

## OpenRouter (Real Cloud Provider)

Used as the primary cloud provider for the L2-05 evaluation.

Example:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-api-key
```

Models configured for runtime switching:
- `liquid/lfm-2.5-2.6b:free`
- `nex-agi/nex-n2.5-mini:free`

## Ollama

Recommended real free/local backend.

Example:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

The model must already exist in the local Ollama installation.

## OpenAI

Optional:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
LLM_MODEL=...
```

## Why an adapter?

It keeps provider-specific configuration out of the graph and lets the same state machine run against different LLM implementations.
