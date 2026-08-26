"""Planner-executor workflow for support-ticket semantic search.

The planner turns a customer issue into a small, inspectable plan. The executor
runs only approved local actions and returns matching historical tickets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "problem_16_semantic_ticket_search"))

from semantic_search import (
    DEFAULT_RESULTS,
    display_results,
    index_tickets,
    load_embedding_model,
    search_tickets,
)


@dataclass(frozen=True)
class PlanStep:
    """One action in an executable support-ticket search plan."""

    name: str
    description: str


@dataclass
class SearchPlan:
    """Inspectable plan created for one customer issue."""

    query: str
    steps: list[PlanStep] = field(default_factory=list)


def create_plan(query: str, n_results: int = DEFAULT_RESULTS) -> SearchPlan:
    """Create a deterministic plan without performing any search."""
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("Please enter a customer issue.")
    if n_results < 1:
        raise ValueError("n_results must be at least 1.")
    return SearchPlan(
        query=cleaned_query,
        steps=[
            PlanStep("validate", "Validate the customer issue."),
            PlanStep("load_model", "Load the local embedding model."),
            PlanStep("index", "Read ticket files and update the persistent local index."),
            PlanStep("search", f"Retrieve the top {n_results} semantic matches."),
            PlanStep("report", "Return ticket IDs, scores, status, and matching text."),
        ],
    )


def execute_plan(
    plan: SearchPlan,
    *,
    model_loader: Callable[[], Any] = load_embedding_model,
) -> dict[str, Any]:
    """Execute a search plan and return a structured, inspectable result."""
    if not plan.query.strip():
        raise ValueError("Please enter a customer issue.")
    model = model_loader()
    collection, ticket_count, chunk_count = index_tickets(model)
    results = search_tickets(plan.query, model, collection)
    return {
        "query": plan.query,
        "ticket_count": ticket_count,
        "chunk_count": chunk_count,
        "results": results,
        "found": bool(results),
    }


def print_plan(plan: SearchPlan) -> None:
    print("\nPLAN")
    for number, step in enumerate(plan.steps, 1):
        print(f"{number}. {step.name}: {step.description}")


def run_planner_executor() -> None:
    print("=" * 60)
    print("PLANNER-EXECUTOR SUPPORT TICKET SEARCH")
    print("=" * 60)
    while True:
        query = input("\nCustomer issue (type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            print("Goodbye.")
            return
        if not query:
            print("Please enter a customer issue.")
            continue
        try:
            plan = create_plan(query)
            print_plan(plan)
            print("\nExecuting plan...")
            result = execute_plan(plan)
            print(f"Indexed tickets: {result['ticket_count']}")
            print(f"Indexed chunks: {result['chunk_count']}")
            display_results(result["query"], result["results"])
        except Exception as exc:
            print(f"Execution failed safely: {exc}")


if __name__ == "__main__":
    run_planner_executor()
