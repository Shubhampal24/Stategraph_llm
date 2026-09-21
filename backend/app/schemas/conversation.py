from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)
    provider: str | None = None
    model: str | None = None


class ResumeRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=100)
    decision: str = Field(min_length=1, max_length=20)
    provider: str | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    thread_id: str
    status: str
    response: str | None = None
    intent: str | None = None
    human_decision: str | None = None
    pending_interrupt: dict | None = None
    trace: list[str]
    state: dict
    next_nodes: list[str]


class ErrorResponse(BaseModel):
    error: dict
