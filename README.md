# StateFlow — L2-05 LangGraph-Based Stateful Conversational Agent

StateFlow is a focused implementation of the OS3 AI Engineer Evaluation Workbook assignment:

**L2-05 — LangGraph-Based Stateful Conversational Agent**

The project demonstrates:

- LangGraph `StateGraph`
- Explicit typed conversation state
- Multiple nodes and edges
- Conditional routing based on intent/state
- Persistent thread-based checkpointing
- Resumable conversations
- Real human-in-the-loop interruption and resume
- Pluggable LLM backends
- Free-first local/mock execution
- Thin FastAPI interface
- Automated tests
- Execution traces and documentation

## Assignment mapping

| OS3 L2-05 requirement | StateFlow implementation |
|---|---|
| LangGraph StateGraph with multiple nodes/edges | `backend/app/graph/graph.py` |
| Conditional routing based on intent/state | `backend/app/graph/routing.py` |
| Persistent checkpointing | PostgreSQL `PostgresSaver` |
| Application history | PostgreSQL `threads` & `messages` |
| Thread-based resumable sessions | `thread_id` in LangGraph config |
| Human-in-the-loop interrupt | `human_approval` node + `interrupt()` |
| Pluggable LLM backend | `backend/app/llm/` |
| LangGraph codebase | `backend/app/graph/` |
| README: graph/state/design | This README + `docs/` |
| Sample execution trace | `docs/EXECUTION_TRACE.md` and `examples/` |

## Scope discipline

This project intentionally does **not** implement:

- RAG
- vector databases or embeddings
- MCP
- multi-agent orchestration
- n8n
- streaming
- complex authentication
- production API gateway architecture
- Redis/Celery/Kubernetes

Those are separate capabilities in the OS3 workbook or are unnecessary for L2-05.

## Architecture

```text
                 ┌──────────────────────┐
                 │     React UI         │
                 │  optional demo UI    │
                 └──────────┬───────────┘
                            │ HTTP
                            ▼
                 ┌──────────────────────┐
                 │      FastAPI         │
                 │    thin API layer    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Conversation Service │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      LangGraph       │
                 │      StateGraph      │
                 └──────────┬───────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        General         Clarify        Human Approval
        Response        Request          INTERRUPT
             │              │              │
             └──────────────┴───────┬──────┘
                                    │
                                  RESUME
                                    │
                                    ▼
                           Final response/state
                                    │
                                    ▼
                         PostgreSQL checkpoint store
                                    &
                         Application Thread History

                     ┌──────────────────────┐
                     │    LLM Adapter       │
                     │ Mock/Ollama/Gemini/  │
                     │ OpenRouter/OpenAI    │
                     └──────────────────────┘
```

## Graph

```text
START
  |
  v
receive_message
  |
  v
analyze_intent
  |
  +----------------------+----------------------+
  |                      |                      |
  v                      v                      v
general_response     clarification       human_approval
  |                      |                      |
  v                      v                  INTERRUPT
 END                     END                     |
                                                RESUME
                                                  |
                                                  v
                                           approval_route
                                             /       \
                                            /         \
                                           v           v
                                  approved_response  rejected_response
                                            \         /
                                             \       /
                                               END
```

## State schema

The graph keeps explicit state rather than hiding all conversation context inside a prompt.

```text
thread_id                 conversation identity
messages                  persisted conversation messages
user_input                current user message
intent                    general / clarification / approval
requires_human_approval   whether the current request needs approval
human_decision            approve / reject after resume
response                  latest assistant response
trace                     human-readable node execution trace
```

See `docs/STATE_SCHEMA.md`.

## LLM backend strategy

The project is free-first.

### Mock backend

Default for automated tests:

```env
LLM_PROVIDER=mock
```

No network and no API key. Validated.

### Ollama backend

Recommended real local demo:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
LLM_MODEL=llama3.2:3b
```

You need Ollama installed locally and a model pulled locally. No paid API is required.

### OpenRouter backend (Real Cloud Provider)

Use any model through OpenRouter using a single API key:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-api-key
```

Model selection occurs at runtime. The currently configured models are:
- `liquid/lfm-2.5-2.6b:free`
- `nex-agi/nex-n2.5-mini:free`

### Google Gemini backend

Use official Gemini SDK:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-1.5-flash
```

### OpenAI backend

Optional only:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
LLM_MODEL=...
```

No cloud key is required for the free/local paths.

### Model selection

The provider and model can be passed dynamically with requests to switch engines mid-conversation, preserving the thread ID and context! The frontend lists supported combinations by querying `/api/models`. Model switching preserves the same thread/state.

## Backend setup

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

If PowerShell blocks activation, use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Start backend

```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health:

```text
http://127.0.0.1:8000/health
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Default Vite URL:

```text
http://localhost:5173
```

The frontend uses:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## API examples

### Normal conversation

```http
POST /api/chat
Content-Type: application/json

{
  "thread_id": "demo-001",
  "message": "Hello, explain Python functions."
}
```

### Approval request

Use a phrase such as:

```text
Please approve this action.
```

The graph will stop at the human approval interrupt.

### Resume

```http
POST /api/resume
Content-Type: application/json

{
  "thread_id": "demo-001",
  "decision": "approve"
}
```

or:

```json
{
  "thread_id": "demo-001",
  "decision": "reject"
}
```

### State

```http
GET /api/state/demo-001
```

## Persistence demonstration

1. Start the backend.
2. Use thread `demo-001`.
3. Send several messages.
4. Stop the backend.
5. Start the backend again.
6. Reuse `demo-001`.
7. Inspect `/api/state/demo-001`.

The graph uses the persisted PostgreSQL checkpoint store, so the thread can be resumed after process restart, and the application stores a historical log of your conversation in the database.

## Testing

Tests use the mock LLM and an isolated PostgreSQL test database (`stateflow_test`).

```powershell
cd backend
python -m pytest -q
```

Tests cover:

- graph compilation
- normal routing
- clarification routing
- approval routing
- checkpoint persistence
- state recovery
- human interrupt
- human resume
- API validation
- API chat flow

## Demo sequence

See:

- `docs/DEMO_SCRIPT.md`
- `docs/EXECUTION_TRACE.md`

The strongest demonstration is:

```text
1. Start thread
2. Send normal message
3. Show persisted state
4. Trigger approval-required request
5. Show graph interruption
6. Approve
7. Resume graph
8. Show final state and trace
9. Restart backend
10. Reopen the same thread
```

## Design decisions

### Why PostgreSQL?

L2-05 requires persistent checkpointing. We upgraded to PostgreSQL for the LangGraph checkpointer (`PostgresSaver`) and application conversation history (`threads` and `messages`), keeping LangGraph's internal state completely isolated from the UI's historical thread log.

### Why no vector database?

Vector memory is a separate OS3 assignment. L2-05 needs stateful checkpointing, not semantic long-term memory.

### Why no MCP?

MCP is a separate OS3 assignment. L2-05 can demonstrate orchestration and human approval without external tool servers.

### Why a thin FastAPI layer?

The assignment does not require REST APIs. The small API makes the graph easy to demonstrate and test without turning the project into a production API-service assignment.

### Why a custom LLM adapter?

The graph should not depend on one provider. The adapter lets the same graph run with mock, local Ollama, or optional OpenAI.

## Security

- Never commit `.env`.
- Never place API keys in source code.
- Never expose secrets in API responses.
- Use synthetic demo data.
- The default test path requires no external credentials.

## Limitations

This is intentionally an evaluation-focused project, not a production multi-tenant platform. It does not implement authentication, distributed checkpoint storage, vector memory, MCP, streaming, or multi-agent orchestration.

Those omissions are deliberate scope boundaries for L2-05.
