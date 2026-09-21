def test_human_approval_interrupt(service):
    result = service.chat(
        "approval-001",
        "Please approve this action before I continue.",
    )

    assert result["status"] == "interrupted"
    assert result["pending_interrupt"]
    assert result["pending_interrupt"]["type"] == "human_approval"
    assert result["next_nodes"]


def test_human_approval_resume(service):
    thread_id = "approval-002"

    interrupted = service.chat(
        thread_id,
        "Please approve this action before I continue.",
    )
    assert interrupted["status"] == "interrupted"

    resumed = service.resume(thread_id, "approve")

    assert resumed["status"] == "completed"
    assert resumed["human_decision"] == "approved"
    assert "approved_response" in resumed["trace"]


def test_human_rejection_resume(service):
    thread_id = "approval-003"

    interrupted = service.chat(
        thread_id,
        "Please approve this action before I continue.",
    )
    assert interrupted["status"] == "interrupted"

    resumed = service.resume(thread_id, "reject")

    assert resumed["status"] == "completed"
    assert resumed["human_decision"] == "rejected"
    assert "rejected_response" in resumed["trace"]
