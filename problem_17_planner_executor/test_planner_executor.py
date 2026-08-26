from planner_executor import create_plan, execute_plan


def test_create_plan_has_search_steps() -> None:
    plan = create_plan("The app keeps logging me out")
    assert plan.query == "The app keeps logging me out"
    assert [step.name for step in plan.steps] == ["validate", "load_model", "index", "search", "report"]


def test_execute_plan_with_fake_model() -> None:
    class FakeModel:
        def encode(self, texts, normalize_embeddings=True):
            return [[1.0, 0.0] for _ in texts]

    result = execute_plan(create_plan("login problem"), model_loader=FakeModel)
    assert result["query"] == "login problem"
    assert result["ticket_count"] == 10
    assert result["chunk_count"] == 10
    assert result["found"] is True
