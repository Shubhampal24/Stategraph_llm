from langgraph.types import interrupt

from ..llm.factory import get_llm
from .state import ConversationState


def receive_message(state: ConversationState):
    text = state.get("user_input", "").strip()
    trace = list(state.get("trace", []))
    trace.append("receive_message")

    return {
        "user_input": text,
        "messages": [{"role": "user", "content": text}],
        "trace": trace,
    }


def analyze_intent(state: ConversationState):
    text = state.get("user_input", "").lower()
    trace = list(state.get("trace", []))
    trace.append("analyze_intent")

    approval_markers = (
        "approve this",
        "requires approval",
        "perform this action",
        "delete",
        "send it",
        "execute",
        "make the change",
    )
    clarification_markers = (
        "do it",
        "that one",
        "continue",
        "fix it",
        "proceed",
    )

    if any(marker in text for marker in approval_markers):
        intent = "approval"
        requires_approval = True
    elif any(marker in text for marker in clarification_markers) and len(text.split()) <= 5:
        intent = "clarification"
        requires_approval = False
    else:
        intent = "general"
        requires_approval = False

    trace.append(f"route_intent:{intent}")

    return {
        "intent": intent,
        "requires_human_approval": requires_approval,
        "human_decision": None,
        "trace": trace,
    }


from langchain_core.runnables import RunnableConfig

def general_response(state: ConversationState, config: RunnableConfig):
    provider = config.get("configurable", {}).get("provider")
    model = config.get("configurable", {}).get("model")
    llm = get_llm(provider, model)
    trace = list(state.get("trace", []))
    trace.append("general_response")

    try:
        content = llm.invoke(list(state.get("messages", [])))
    except Exception as exc:
        raise RuntimeError(f"LLM backend failed: {type(exc).__name__}") from exc

    return {
        "messages": [{"role": "assistant", "content": content}],
        "response": content,
        "trace": trace,
    }


def clarification(state: ConversationState):
    text = (
        "I need a little more detail before I can continue. "
        "What would you like me to do?"
    )
    trace = list(state.get("trace", []))
    trace.append("clarification")

    return {
        "messages": [{"role": "assistant", "content": text}],
        "response": text,
        "trace": trace,
    }


def human_approval(state: ConversationState):
    trace = list(state.get("trace", []))
    trace.append("human_approval")

    decision = interrupt(
        {
            "type": "human_approval",
            "thread_id": state.get("thread_id"),
            "message": "This request requires human approval. Approve or reject it.",
            "requested_action": state.get("user_input"),
            "allowed_decisions": ["approve", "reject"],
        }
    )

    decision_str = str(decision).strip().lower()
    if decision_str == "approve":
        normalized = "approved"
    else:
        normalized = "rejected"

    return {
        "human_decision": normalized,
        "trace": trace + [f"human_decision:{normalized}"],
    }


def approved_response(state: ConversationState):
    text = (
        "Approved. The requested action is authorized. "
        "For this evaluation project, no external side effect is performed."
    )
    trace = list(state.get("trace", []))
    trace.append("approved_response")

    return {
        "messages": [{"role": "assistant", "content": text}],
        "response": text,
        "trace": trace,
    }


def rejected_response(state: ConversationState):
    text = "The request was not approved, so no action was taken."
    trace = list(state.get("trace", []))
    trace.append("rejected_response")

    return {
        "messages": [{"role": "assistant", "content": text}],
        "response": text,
        "trace": trace,
    }
