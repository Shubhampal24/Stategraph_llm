def test_graph_builds(service):
    assert service.graph is not None


def test_general_route(service):
    result = service.chat("general-001", "Explain what a Python function is.")
    assert result["status"] == "completed"
    assert result["intent"] == "general"
    assert "general_response" in result["trace"]
    assert result["response"]


def test_clarification_route(service):
    result = service.chat("clarify-001", "Do it")
    assert result["status"] == "completed"
    assert result["intent"] == "clarification"
    assert "clarification" in result["trace"]
    assert result["response"]
