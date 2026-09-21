from ..core.config import settings
from .mock import MockLLM
from .ollama import OllamaLLM
from .openai_backend import OpenAIBackend
from .openrouter import OpenRouterLLM
from .gemini import GeminiLLM

def get_llm(provider: str | None = None, model: str | None = None):
    provider = (provider or settings.llm_provider).lower()

    if provider == "mock":
        return MockLLM(model or settings.llm_model)

    if provider == "ollama":
        return OllamaLLM(settings.ollama_base_url, model or settings.llm_model)
        
    if provider == "openrouter":
        return OpenRouterLLM(settings.openrouter_api_key, model or settings.openrouter_model)
        
    if provider == "gemini":
        return GeminiLLM(settings.gemini_api_key, model or settings.gemini_model)

    if provider == "openai":
        return OpenAIBackend(settings.openai_api_key, model or settings.llm_model)

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER={provider!r}. "
        "Use mock, ollama, openrouter, gemini, or openai."
    )
