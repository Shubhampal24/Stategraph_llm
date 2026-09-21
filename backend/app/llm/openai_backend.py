from openai import OpenAI


class OpenAIBackend:
    provider = "openai"

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai."
            )
        self.model = model
        self.client = OpenAI(api_key=api_key, max_retries=0)

    def invoke(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI returned an empty response.")
        return content
