from .state import ConversationState


def route_after_intent(state: ConversationState) -> str:
    if state.get("requires_human_approval"):
        return "human_approval"

    if state.get("intent") == "clarification":
        return "clarification"

    return "general_response"


def route_after_approval(state: ConversationState) -> str:
    if state.get("human_decision") == "approve":
        return "approved_response"

    return "rejected_response"
