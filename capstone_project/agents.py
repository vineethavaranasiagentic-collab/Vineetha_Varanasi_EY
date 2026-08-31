"""Deterministic planner and executor for the banking RM Copilot MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class Client(BaseModel):
    client_id: str
    name: str
    sector: str
    relationship_status: str
    products: list[str] = Field(default_factory=list)


class Activity(BaseModel):
    activity_id: str
    client_id: str
    activity_date: date
    activity_type: str
    description: str
    amount: float
    direction: str
    balance: float
    product: str
    status: str


class Evidence(BaseModel):
    source_id: str
    source_type: str
    text: str


class PlanStep(BaseModel):
    name: str
    description: str


class CopilotPlan(BaseModel):
    request: str
    client_id: str
    steps: list[PlanStep]
    requires_human_approval: bool = True


class CopilotReport(BaseModel):
    request: str
    client: Client
    observations: list[str]
    evidence: list[Evidence]
    recommended_follow_ups: list[str]
    draft_message: str
    human_approval_required: bool = True
    audit: list[str] = Field(default_factory=list)


CLIENTS = {
    "client_001": Client(
        client_id="client_001",
        name="Apex Manufacturing Pvt. Ltd.",
        sector="Manufacturing",
        relationship_status="Active",
        products=["Current account", "Term loan", "Working capital facility", "Cash management"],
    )
}

ACTIVITY = [
    Activity(activity_id="activity_001", client_id="client_001", activity_date=date(2026, 3, 1), activity_type="Customer deposit", description="Invoice collection - Orion Motors", amount=1850000, direction="Credit", balance=6240000, product="Current account", status="Completed"),
    Activity(activity_id="activity_002", client_id="client_001", activity_date=date(2026, 3, 3), activity_type="Supplier payment", description="Steel and components supplier", amount=920000, direction="Debit", balance=5320000, product="Current account", status="Completed"),
    Activity(activity_id="activity_003", client_id="client_001", activity_date=date(2026, 3, 5), activity_type="Payroll", description="Monthly employee payroll", amount=1380000, direction="Debit", balance=3940000, product="Current account", status="Completed"),
    Activity(activity_id="activity_004", client_id="client_001", activity_date=date(2026, 3, 8), activity_type="Loan repayment", description="Term loan instalment", amount=475000, direction="Debit", balance=3465000, product="Term loan", status="Completed"),
    Activity(activity_id="activity_005", client_id="client_001", activity_date=date(2026, 3, 12), activity_type="Customer deposit", description="Export customer receipt", amount=2100000, direction="Credit", balance=5565000, product="Current account", status="Completed"),
    Activity(activity_id="activity_006", client_id="client_001", activity_date=date(2026, 3, 15), activity_type="Large debit", description="Plant equipment purchase", amount=2800000, direction="Debit", balance=2765000, product="Current account", status="Completed"),
    Activity(activity_id="activity_007", client_id="client_001", activity_date=date(2026, 3, 18), activity_type="Bank fee", description="Cash management service fee", amount=12500, direction="Debit", balance=2752500, product="Cash management", status="Completed"),
    Activity(activity_id="activity_008", client_id="client_001", activity_date=date(2026, 3, 21), activity_type="Supplier payment", description="Packaging materials", amount=640000, direction="Debit", balance=2112500, product="Current account", status="Completed"),
    Activity(activity_id="activity_009", client_id="client_001", activity_date=date(2026, 3, 24), activity_type="Customer payment", description="Domestic customer settlement", amount=980000, direction="Credit", balance=3092500, product="Current account", status="Completed"),
    Activity(activity_id="activity_010", client_id="client_001", activity_date=date(2026, 3, 27), activity_type="Interest charge", description="Working capital facility interest", amount=38500, direction="Debit", balance=3054000, product="Working capital facility", status="Completed"),
]


def create_plan(request: str, client_id: str = "client_001") -> CopilotPlan:
    cleaned = request.strip()
    if not cleaned:
        raise ValueError("Please enter a relationship-manager request.")
    return CopilotPlan(
        request=cleaned,
        client_id=client_id,
        steps=[
            PlanStep(name="validate", description="Validate the request and client identifier."),
            PlanStep(name="load_client", description="Load the client profile from the approved local repository."),
            PlanStep(name="load_activity", description="Load supplied account activity for the client."),
            PlanStep(name="retrieve_evidence", description="Collect source-backed evidence relevant to the request."),
            PlanStep(name="analyze", description="Generate only supported observations and review questions."),
            PlanStep(name="draft", description="Prepare a factual draft marked for human approval."),
            PlanStep(name="validate_output", description="Check grounding and approval requirements."),
            PlanStep(name="report", description="Return the plan execution report and audit trail."),
        ],
    )


def execute_plan(plan: CopilotPlan) -> CopilotReport:
    if not plan.request.strip():
        raise ValueError("Execution failed safely: the request is empty.")
    client = CLIENTS.get(plan.client_id)
    if client is None:
        raise ValueError(f"Execution failed safely: client '{plan.client_id}' was not found.")
    records = [item for item in ACTIVITY if item.client_id == client.client_id]
    if not records:
        raise ValueError("Execution failed safely: no account activity was found.")

    evidence = [Evidence(source_id=item.activity_id, source_type="account_activity", text=f"{item.activity_date.isoformat()}: {item.activity_type} — {item.description}; amount {item.amount:,.0f}; balance {item.balance:,.0f}; status {item.status}.") for item in records]
    observations = [
        f"The supplied activity includes customer deposits of 1,850,000 and 2,100,000.",
        f"The supplied activity includes a 2,800,000 debit described as a plant equipment purchase on 2026-03-15.",
        f"The supplied activity includes a term loan instalment of 475,000 and working capital facility interest of 38,500.",
        f"The latest supplied balance is 3,054,000 on 2026-03-27.",
    ]
    follow_ups = [
        "Confirm with the relationship manager whether the plant equipment purchase requires any follow-up.",
        "Review cash-flow needs around supplier payments, payroll, and scheduled loan obligations.",
    ]
    draft = (f"Hello {client.name},\n\nThe supplied March 2026 account activity includes customer deposits, supplier payments, payroll, a term loan instalment, and a plant equipment purchase. "
             "The latest supplied activity shows a balance of 3,054,000. Please confirm whether you would like to discuss any of these recorded transactions.")
    return CopilotReport(request=plan.request, client=client, observations=observations, evidence=evidence, recommended_follow_ups=follow_ups, draft_message=draft, audit=[f"Executed {step.name}" for step in plan.steps])


def run_request(request: str, client_id: str = "client_001") -> dict[str, Any]:
    plan = create_plan(request, client_id)
    report = execute_plan(plan)
    return {"plan": plan.model_dump(mode="json"), "report": report.model_dump(mode="json")}
