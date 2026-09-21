# Start Here — StateFlow L2-05

## 1. Install

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## 2. Run tests first

```powershell
python -m pytest -q
```

The test suite uses the mock LLM and does not require an API key.

## 3. Run backend

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 4. Run frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

## 5. Read these in order

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/STATE_SCHEMA.md`
4. `docs/GRAPH_FLOW.md`
5. `docs/CHECKPOINTING.md`
6. `docs/HUMAN_IN_LOOP.md`
7. `docs/LLM_BACKENDS.md`
8. `docs/EXECUTION_TRACE.md`
9. `docs/DEMO_SCRIPT.md`

## 6. Interview sentence

> StateFlow uses LangGraph StateGraph to manage explicit conversational state. The graph conditionally routes requests by intent, persists state by thread using PostgreSQL checkpointing, and pauses at a human approval node using LangGraph interrupt/resume semantics. The LLM is behind a provider adapter so the graph can run with a mock backend, local Ollama, or optional OpenAI.
