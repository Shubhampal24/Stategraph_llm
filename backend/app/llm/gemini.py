from google import genai
from google.genai import types

from .base import LLMBackend

class GeminiLLM(LLMBackend):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        
        self.provider = "gemini"
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def invoke(self, messages: list[dict[str, str]]) -> str:
        # Convert standard messages to Gemini contents
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
            )
            return response.text if response.text else ""
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}") from e
