def test_thread_state_persists(service):
    thread_id = "persist-001"

    first = service.chat(thread_id, "My favorite language is Python.")
    assert first["status"] == "completed"

    state = service.state(thread_id)

    assert state["thread_id"] == thread_id
    assert state["values"]["messages"]
    assert state["values"]["user_input"] == "My favorite language is Python."


def test_new_service_can_read_existing_checkpoint(monkeypatch):
    from app.graph.checkpoint import create_checkpointer
    from app.graph.graph import build_graph
    from app.services.conversation_service import create_conversation_service

    from app.core.config import settings

    service_one = create_conversation_service(
        build_graph(create_checkpointer(settings.test_database_url))
    )
    service_one.chat("restart-001", "Remember that I use Python.")

    service_two = create_conversation_service(
        build_graph(create_checkpointer(settings.test_database_url))
    )

    state = service_two.state("restart-001")

    assert state["values"]["thread_id"] == "restart-001"
    assert state["values"]["messages"]
