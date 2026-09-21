from typing import Annotated, Literal
from typing_extensions import TypedDict


Intent = Literal["general", "clarification", "approval"]


def append_messages(
    existing: list[dict[str, str]] | None,
    updates: list[dict[str, str]] | None,
) -> list[dict[str, str]]:
    return list(existing or []) + list(updates or [])


class ConversationState(TypedDict, total=False):
    thread_id: str
    messages: Annotated[list[dict[str, str]], append_messages]
    user_input: str
    intent: Intent
    requires_human_approval: bool
    human_decision: str | None
    response: str | None
    trace: list[str]
