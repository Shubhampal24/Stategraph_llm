def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_empty_message(client):
    response = client.post(
        "/api/chat",
        json={"thread_id": "api-001", "message": ""},
    )
    assert response.status_code == 422


def test_chat(client):
    response = client.post(
        "/api/chat",
        json={
            "thread_id": "api-002",
            "message": "Hello from the API.",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["thread_id"] == "api-002"
    assert data["status"] == "completed"
    assert data["response"]


def test_approval_and_resume(client):
    thread_id = "api-003"

    response = client.post(
        "/api/chat",
        json={
            "thread_id": thread_id,
            "message": "Please approve this action.",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "interrupted"

    response = client.post(
        "/api/resume",
        json={
            "thread_id": thread_id,
            "decision": "approve",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["human_decision"] == "approve"


def test_state_endpoint(client):
    response = client.post(
        "/api/chat",
        json={
            "thread_id": "api-004",
            "message": "Store this thread state.",
        },
    )
    assert response.status_code == 200

    response = client.get("/api/state/api-004")
    assert response.status_code == 200
    assert response.json()["thread_id"] == "api-004"
    assert response.json()["values"]["messages"]
