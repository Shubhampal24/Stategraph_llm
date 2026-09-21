from openai import OpenAI

from .base import LLMBackend

class OpenRouterLLM(LLMBackend):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        
        self.provider = "openrouter"
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def invoke(self, messages: list[dict[str, str]]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {e}") from e
