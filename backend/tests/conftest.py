import os

import pytest
from fastapi.testclient import TestClient

os.environ["LLM_PROVIDER"] = "mock"
os.environ["LLM_MODEL"] = "test-model"

from app.graph.checkpoint import create_checkpointer  # noqa: E402
from app.graph.graph import build_graph  # noqa: E402
from app.services.conversation_service import create_conversation_service  # noqa: E402
from app.main import app  # noqa: E402


from app.core.config import settings

@pytest.fixture()
def service():
    checkpointer = create_checkpointer(settings.test_database_url)
    graph = build_graph(checkpointer)
    return create_conversation_service(graph)


@pytest.fixture()
def client(monkeypatch):
    import app.main as main_module

    checkpointer = create_checkpointer(settings.test_database_url)
    graph = build_graph(checkpointer)

    monkeypatch.setattr(
        main_module,
        "conversation_service",
        create_conversation_service(graph),
    )

    with TestClient(app) as test_client:
        yield test_client

