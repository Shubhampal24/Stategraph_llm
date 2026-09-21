import pytest
import httpx
import uuid
from fastapi.testclient import TestClient
from app.main import app

def test_thread_repository_and_api(client):
    # 1. create thread implicitly by sending a message
    thread_id = "hist-test-" + str(uuid.uuid4())
    
    # Send first message
    r1 = client.post("/api/chat", json={
        "thread_id": thread_id,
        "message": "First message to set title",
        "provider": "mock",
        "model": "mock-model"
    })
    assert r1.status_code == 200
    
    # 2. list threads
    r_list = client.get("/api/threads")
    assert r_list.status_code == 200
    threads = r_list.json()
    assert any(t["thread_id"] == thread_id for t in threads)
    
    # 6. first-message title
    thread = next(t for t in threads if t["thread_id"] == thread_id)
    assert thread["title"] == "First message to set title"
    
    # Send second message
    r2 = client.post("/api/chat", json={
        "thread_id": thread_id,
        "message": "Second message",
        "provider": "mock",
        "model": "mock-model"
    })
    assert r2.status_code == 200
    
    # 7. title does not change on later messages
    r_list2 = client.get("/api/threads")
    thread2 = next(t for t in r_list2.json() if t["thread_id"] == thread_id)
    assert thread2["title"] == "First message to set title"
    
    # 3. get thread & 4. get thread messages
    r_get = client.get(f"/api/threads/{thread_id}")
    assert r_get.status_code == 200
    t_data = r_get.json()
    assert t_data["title"] == "First message to set title"
    messages = t_data["messages"]
    
    # 8. user message stored once, 9. assistant message stored once
    assert len(messages) == 4
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "First message to set title"
    assert messages[1]["role"] == "assistant"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "Second message"
    assert messages[3]["role"] == "assistant"
    
    # 5. nonexistent thread returns 404
    r_404 = client.get("/api/threads/does-not-exist")
    assert r_404.status_code == 404

def test_model_switch_preserves_thread_id(client):
    thread_id = "hist-test-" + str(uuid.uuid4())
    
    r1 = client.post("/api/chat", json={
        "thread_id": thread_id,
        "message": "Hello",
        "provider": "mock",
        "model": "mock-model"
    })
    
    # simulate switching provider/model
    import app.api.chat
    app.api.chat.SUPPORTED_PROVIDERS["mock"].append("mock-model-2")
    r2 = client.post("/api/chat", json={
        "thread_id": thread_id,
        "message": "Hello again",
        "provider": "mock",
        "model": "mock-model-2"
    })
    app.api.chat.SUPPORTED_PROVIDERS["mock"].remove("mock-model-2")
    
    # Verify same thread_id is preserved
    r_get = client.get(f"/api/threads/{thread_id}")
    assert r_get.status_code == 200
    messages = r_get.json()["messages"]
    assert len(messages) == 4
