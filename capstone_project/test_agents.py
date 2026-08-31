from agents import create_plan, execute_plan


def test_plan_has_ordered_agent_steps():
    plan = create_plan("Review March activity")
    assert [step.name for step in plan.steps] == [
        "validate", "load_client", "load_activity", "retrieve_evidence",
        "analyze", "draft", "validate_output", "report",
    ]


def test_executor_returns_grounded_report():
    result = execute_plan(create_plan("Review March activity"))
    assert result.client.client_id == "client_001"
    assert len(result.evidence) == 10
    assert result.human_approval_required is True


def test_empty_request_fails_safely():
    try:
        create_plan(" ")
    except ValueError as exc:
        assert "Please enter" in str(exc)
    else:
        raise AssertionError("Expected empty request to fail")
