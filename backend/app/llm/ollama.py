import json
from urllib import request
from urllib.error import HTTPError, URLError


class OllamaLLM:
    provider = "ollama"

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def invoke(self, messages: list[dict[str, str]]) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "stream": False,
            }
        ).encode("utf-8")

        req = request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama provider error ({exc.code}): {body[:300]}") from exc
        except URLError as exc:
            raise RuntimeError(
                "Could not connect to Ollama. Make sure Ollama is running."
            ) from exc

        message = data.get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("Ollama returned an empty response.")
        return content
