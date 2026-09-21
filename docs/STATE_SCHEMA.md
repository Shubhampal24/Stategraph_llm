# State Schema

StateFlow uses an explicit `ConversationState`.

| Field | Meaning |
|---|---|
| `thread_id` | Persistent conversation identifier |
| `messages` | Ordered user/assistant messages |
| `user_input` | Current user input |
| `intent` | Routing classification |
| `requires_human_approval` | Whether the approval branch is required |
| `human_decision` | `approve` or `reject` after resume |
| `response` | Latest assistant response |
| `trace` | Human-readable node transition trace |

## Why explicit state?

The assignment specifically asks for explicit state management. Keeping the fields visible makes the graph easier to reason about, test, debug, and explain during an interview.

## State lifecycle

```text
new message
   ↓
receive_message
   ↓
analyze_intent
   ↓
state.intent
state.requires_human_approval
   ↓
conditional route
   ↓
node updates state
   ↓
checkpoint
```

## Thread identity

`thread_id` is not merely a UI label. It is supplied to LangGraph's configurable execution context so the checkpointer can associate state with the correct conversation.
