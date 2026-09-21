# Graph Flow

## Full graph

```text
START
  ↓
receive_message
  ↓
analyze_intent
  ├── general ─────────────→ general_response ─→ END
  │
  ├── clarification ───────→ clarification ───→ END
  │
  └── approval ─────────────→ human_approval
                                  ↓
                              INTERRUPT
                                  ↓
                               RESUME
                                  ↓
                           approval routing
                              /       \
                             /         \
                            ↓           ↓
                    approved_response  rejected_response
                            \           /
                             \         /
                                END
```

## Routing

`route_after_intent()` examines:

- `requires_human_approval`
- `intent`

It returns a graph destination.

`route_after_approval()` examines `human_decision`.

## Why conditional edges?

They demonstrate that the graph can select a different path from the same node based on state.

## Example

Input:

```text
Please approve this action.
```

State:

```text
intent = approval
requires_human_approval = true
```

Route:

```text
analyze_intent → human_approval
```

The graph then interrupts.

After:

```text
approve
```

the graph resumes and routes to:

```text
approved_response
```
