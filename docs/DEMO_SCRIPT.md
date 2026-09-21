# Interview Demo Script

## Demo 1 — Explain architecture

Say:

> StateFlow uses a LangGraph StateGraph with explicit conversation state. Each message enters the graph, the intent is analyzed, and a conditional edge selects the appropriate node.

Show:

```text
docs/GRAPH_FLOW.md
```

## Demo 2 — Normal conversation

Thread:

```text
demo-001
```

Message:

```text
Explain what a Python function is.
```

Show the response and trace.

## Demo 3 — State persistence

Send:

```text
My preferred language is Python.
```

Then inspect:

```text
GET /api/state/demo-001
```

Point out the persisted state and thread ID.

## Demo 4 — Human interrupt

Send:

```text
Please approve this action.
```

Show:

```text
analyze_intent
→ human_approval
→ INTERRUPT
```

## Demo 5 — Resume

Approve:

```text
POST /api/resume
{
  "thread_id": "demo-001",
  "decision": "approve"
}
```

Show:

```text
RESUME
→ approved_response
→ END
```

## Demo 6 — Restart

Stop and restart the backend.

Reuse the same thread.

Show that the checkpoint is still available.

## Demo 7 — Tests

Run:

```powershell
cd backend
python -m pytest -q
```

Explain that tests use the mock backend and are independent of paid APIs.
