# Sample Execution Trace

## Scenario 1 — Normal

```text
Thread: demo-normal

START
→ receive_message
→ analyze_intent
  intent=general
→ general_response
→ END
```

## Scenario 2 — Clarification

```text
Thread: demo-clarification

START
→ receive_message
→ analyze_intent
  intent=clarification
→ clarification
→ END
```

## Scenario 3 — Human approval

```text
Thread: demo-approval

START
→ receive_message
→ analyze_intent
  intent=approval
  requires_human_approval=true
→ human_approval
→ INTERRUPT

Human:
  approve

RESUME
→ human_approval returns approve
→ approved_response
→ END
```

## Scenario 4 — Rejection

```text
Thread: demo-rejection

START
→ receive_message
→ analyze_intent
  intent=approval
→ human_approval
→ INTERRUPT

Human:
  reject

RESUME
→ rejected_response
→ END
```

## Scenario 5 — Restart/resume

```text
Process A
→ thread=demo-restart
→ message
→ checkpoint

Process A stops

Process B
→ thread=demo-restart
→ load checkpoint
→ inspect state
→ continue conversation
```
