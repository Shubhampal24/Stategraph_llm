# Persistent Checkpointing

## Requirement

L2-05 requires persistent checkpointing with thread-based state and resumable sessions.

## Implementation

StateFlow uses:

```text
LangGraph
We use the `PostgresSaver` class provided by `langgraph-checkpoint-postgres`.

It connects to a PostgreSQL database (`stateflow_checkpoints` via the connection pool) and stores checkpoints keyed by thread ID and thread timestamp.
```

## Thread configuration

Each execution receives:

```python
{
    "configurable": {
        "thread_id": "demo-001"
    }
}
```

The checkpointer uses the thread identifier to separate conversations.

## Restart demonstration

```text
Application process A
    ↓
thread demo-001
    ↓
state changes
    ↓
checkpoint saved
    ↓
process stops

Application process B
    ↓
thread demo-001
    ↓
checkpoint loaded
    ↓
conversation resumes
```

## Why SQLite?

It is durable and local, requires no paid service, and is sufficient for an evaluation-scale project. A distributed database could be introduced for a production deployment, but that is outside this assignment's required scope.
