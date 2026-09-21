from typing import Any

from langgraph.types import Command

from ..core.config import settings
from ..graph.graph import build_graph


class ConversationService:
    def __init__(self, graph):
        self.graph = graph

    @staticmethod
    def config(thread_id: str, provider: str | None = None, model: str | None = None) -> dict[str, Any]:
        return {"configurable": {"thread_id": thread_id, "provider": provider, "model": model}}

    def chat(self, thread_id: str, message: str, provider: str | None = None, model: str | None = None) -> dict[str, Any]:
        result = self.graph.invoke(
            {
                "thread_id": thread_id,
                "user_input": message,
                "trace": [],
            },
            self.config(thread_id, provider, model),
        )
        return self._normalize_result(thread_id, result)

    def resume(self, thread_id: str, decision: str, provider: str | None = None, model: str | None = None) -> dict[str, Any]:
        result = self.graph.invoke(
            Command(resume=decision),
            self.config(thread_id, provider, model),
        )
        return self._normalize_result(thread_id, result)

    def state(self, thread_id: str) -> dict[str, Any]:
        snapshot = self.graph.get_state(self.config(thread_id))
        values = dict(snapshot.values or {})

        pending_interrupt = False
        for task in snapshot.tasks:
            if getattr(task, "interrupts", ()):
                pending_interrupt = True
                break

        return {
            "thread_id": thread_id,
            "values": values,
            "next_nodes": list(snapshot.next),
            "pending_interrupt": pending_interrupt,
        }

    def _normalize_result(self, thread_id: str, result: dict[str, Any]) -> dict[str, Any]:
        interrupt_items = result.get("__interrupt__", [])
        pending = []

        for item in interrupt_items:
            value = getattr(item, "value", item)
            pending.append(value)

        state = self.state(thread_id)
        values = state["values"]

        return {
            "thread_id": thread_id,
            "status": "interrupted" if pending else "completed",
            "response": values.get("response"),
            "intent": values.get("intent"),
            "human_decision": values.get("human_decision"),
            "pending_interrupt": pending[0] if pending else None,
            "trace": values.get("trace", []),
            "state": values,
            "next_nodes": state["next_nodes"],
        }


def create_conversation_service(graph):
    return ConversationService(graph)
