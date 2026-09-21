# Architecture

## Purpose

StateFlow is deliberately centered on the L2-05 requirements rather than trying to become a generic AI platform.

## Layers

```text
Frontend
   ↓
FastAPI
   ↓
ConversationService
   ↓
LangGraph StateGraph
   ↓
LLM Adapter
   ↓
Mock / Ollama / OpenAI

LangGraph Checkpointer
   ↓
SQLite
```

## Why the graph is the core

A normal chatbot could perform:

```text
message → LLM → response
```

StateFlow instead performs:

```text
message
  ↓
state update
  ↓
intent analysis
  ↓
conditional edge
  ↓
selected node
  ↓
state update
  ↓
checkpoint
```

This makes orchestration explicit and inspectable.

## Nodes

1. `receive_message`
2. `analyze_intent`
3. `general_response`
4. `clarification`
5. `human_approval`
6. `approved_response`
7. `rejected_response`

## Edges

The graph uses:

- normal edges
- conditional edges
- `START`
- `END`
- interrupt/resume behavior

## Supporting API

FastAPI is intentionally thin. It exists to make the graph easy to run and demonstrate. It is not intended to satisfy a separate production API assignment.

## Persistence

**PostgreSQL**: Stores persistent conversation history (`threads` and `messages`), and persistent LangGraph checkpoint state using `PostgresSaver`. A thread ID is supplied through LangGraph's configurable runtime context.
Application persistence (history) is also stored in PostgreSQL, but using separate tables (`threads` and `messages`), completely isolated from the checkpoints.

This makes a conversation resumable after application restart.

## Scope boundary

No RAG, MCP, vector database, multi-agent system, or streaming layer is included because those capabilities are outside the focused L2-05 implementation.
