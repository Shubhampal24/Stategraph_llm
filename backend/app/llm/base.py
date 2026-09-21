from typing import Protocol


class LLMBackend(Protocol):
    provider: str
    model: str

    def invoke(self, messages: list[dict[str, str]]) -> str:
        ...
