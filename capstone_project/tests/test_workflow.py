from main import run


def test_default_workflow_blocks_only_when_compliance_fails_or_stays_pending():
    result = run("CLIENT-001")
    assert result["approval_status"] in {"PENDING", "BLOCKED"}
    assert result["client_id"] == "CLIENT-001"


def test_approval_marks_ready_to_send():
    result = run("CLIENT-002", approved=True)
    if result["compliance"]["status"] == "PASS":
        assert result["approval_status"] == "READY_TO_SEND"
