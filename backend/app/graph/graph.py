from langgraph.graph import END, START, StateGraph

from .nodes import (
    analyze_intent,
    approved_response,
    clarification,
    general_response,
    human_approval,
    receive_message,
    rejected_response,
)
from .routing import route_after_approval, route_after_intent
from .state import ConversationState


def build_graph(checkpointer):
    builder = StateGraph(ConversationState)

    builder.add_node("receive_message", receive_message)
    builder.add_node("analyze_intent", analyze_intent)
    builder.add_node("general_response", general_response)
    builder.add_node("clarification", clarification)
    builder.add_node("human_approval", human_approval)
    builder.add_node("approved_response", approved_response)
    builder.add_node("rejected_response", rejected_response)

    builder.add_edge(START, "receive_message")
    builder.add_edge("receive_message", "analyze_intent")

    builder.add_conditional_edges(
        "analyze_intent",
        route_after_intent,
        {
            "general_response": "general_response",
            "clarification": "clarification",
            "human_approval": "human_approval",
        },
    )

    builder.add_edge("general_response", END)
    builder.add_edge("clarification", END)

    builder.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "approved_response": "approved_response",
            "rejected_response": "rejected_response",
        },
    )

    builder.add_edge("approved_response", END)
    builder.add_edge("rejected_response", END)

    return builder.compile(checkpointer=checkpointer)
