# Human-in-the-Loop

## Purpose

L2-05 requires human-in-the-loop interrupt handling for at least one node.

StateFlow uses the `human_approval` node.

## Flow

```text
User request
   ↓
analyze_intent
   ↓
approval required
   ↓
human_approval
   ↓
interrupt()
   ↓
graph pauses
```

The interrupt payload identifies:

- type
- thread ID
- requested action
- allowed decisions

## Resume

The API sends:

```json
{
  "thread_id": "demo-001",
  "decision": "approve"
}
```

The service resumes the same graph thread with a LangGraph `Command(resume=...)`.

## Approval

```text
approve
 ↓
approved_response
 ↓
END
```

## Rejection

```text
reject
 ↓
rejected_response
 ↓
END
```

## Important safety boundary

The demo does not perform an external side effect after approval. Approval is used to demonstrate the orchestration mechanism without creating accidental real-world actions.
