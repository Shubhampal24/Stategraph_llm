# Interview Notes

## What is LangGraph?

LangGraph is used to model stateful, graph-based application workflows where nodes perform work and edges determine what happens next.

## Why StateGraph?

Because the assignment requires explicit state and graph orchestration. `StateGraph` makes the state transitions and routing structure explicit.

## What is a node?

A node is a unit of work that reads graph state and returns state updates.

Examples:

- receive message
- analyze intent
- generate response
- request human approval

## What is an edge?

An edge determines which node executes next.

## What is a conditional edge?

A conditional edge chooses the destination using current state.

## What is checkpointing?

Checkpointing persists graph state so a thread can be inspected or resumed later.

## Why thread_id?

It gives the checkpointer a stable identity for a conversation.

## What is human-in-the-loop?

The graph intentionally pauses at an approval node and waits for a human decision before continuing.

## What happens on interrupt?

Execution is suspended and the current graph state is persisted. A later resume operation supplies the human decision.

## Why not vector memory?

Because vector memory is a different problem: semantic retrieval of older information. This assignment requires persistent graph state, not vector search.

## Why not MCP?

MCP is a separate OS3 assignment. It would add tool-server complexity without helping demonstrate the required L2-05 capabilities.

## Why mock LLM?

It makes automated tests deterministic and free.

## Why Ollama?

It provides a local path that does not require paid API credits.

## Why is FastAPI included?

Only as a thin demonstration and testing interface. The graph remains the main artifact.

## Main design principle

Keep the orchestration logic independent from the LLM provider.
