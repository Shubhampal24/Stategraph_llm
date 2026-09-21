import pytest
from fastapi.testclient import TestClient
from app.llm.factory import get_llm
from app.llm.mock import MockLLM
from app.llm.ollama import OllamaLLM
from app.llm.openrouter import OpenRouterLLM
from app.llm.gemini import GeminiLLM
from unittest.mock import patch
from app.core.config import Settings

def test_mock_provider_creation():
    llm = get_llm("mock", "test-model")
    assert isinstance(llm, MockLLM)
    assert llm.model == "test-model"

def test_ollama_provider_creation():
    llm = get_llm("ollama", "test-model")
    assert isinstance(llm, OllamaLLM)
    assert llm.model == "test-model"

def test_openrouter_validation(monkeypatch):
    # Test missing key
    monkeypatch.setattr("app.llm.factory.settings", Settings(openrouter_api_key=""))
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY is not configured"):
        get_llm("openrouter", "test-model")
        
    # Test valid key
    monkeypatch.setattr("app.llm.factory.settings", Settings(openrouter_api_key="fake-key"))
    llm = get_llm("openrouter", "test-model")
    assert isinstance(llm, OpenRouterLLM)
    assert llm.model == "test-model"

def test_gemini_validation(monkeypatch):
    # Test missing key
    monkeypatch.setattr("app.llm.factory.settings", Settings(gemini_api_key=""))
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        get_llm("gemini", "test-model")
        
    # Test valid key
    monkeypatch.setattr("app.llm.factory.settings", Settings(gemini_api_key="fake-key"))
    llm = get_llm("gemini", "test-model")
    assert isinstance(llm, GeminiLLM)
    assert llm.model == "test-model"

def test_invalid_provider_rejected(client):
    response = client.post(
        "/api/chat",
        json={"thread_id": "p-1", "message": "Hi", "provider": "invalid_p"}
    )
    assert response.status_code == 400
    assert "Invalid provider" in response.json()["detail"]

def test_invalid_model_rejected(client):
    response = client.post(
        "/api/chat",
        json={"thread_id": "p-2", "message": "Hi", "provider": "mock", "model": "invalid-model"}
    )
    assert response.status_code == 400
    assert "Invalid model" in response.json()["detail"]

def test_model_switching_preserves_thread_id(client):
    import app.api.chat
    app.api.chat.SUPPORTED_PROVIDERS["mock"].append("mock-model-2")
    
    r1 = client.post(
        "/api/chat",
        json={"thread_id": "switch-1", "message": "Hi", "provider": "mock", "model": "mock-model"}
    )
    assert r1.status_code == 200
    
    r2 = client.post(
        "/api/chat",
        json={"thread_id": "switch-1", "message": "Hello again", "provider": "mock", "model": "mock-model-2"}
    )
    assert r2.status_code == 200
    
    r3 = client.get("/api/state/switch-1")
    assert r3.status_code == 200
    state = r3.json()
    
    assert state["thread_id"] == "switch-1"
    
    user_messages = [m["content"] for m in state["values"]["messages"] if m["role"] == "user"]
    assert "Hi" in user_messages
    assert "Hello again" in user_messages

    app.api.chat.SUPPORTED_PROVIDERS["mock"].remove("mock-model-2")
