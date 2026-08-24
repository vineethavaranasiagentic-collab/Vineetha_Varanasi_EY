from __future__ import annotations

import json
from pathlib import Path

from agents.communication_agent import draft_communication
from agents.meeting_brief_agent import create_meeting_brief
from agents.next_best_action_agent import generate_next_best_action
from agents.opportunity_agent import identify_opportunities
from agents.rag_agent import retrieve_supporting_evidence
from agents.risk_agent import create_risk_alerts
from config import DATA_DIR
from services.approval import approve
from services.client_profile import build_client_profile
from services.compliance import check_compliance
from services.data_loader import DataLoader


def run(client_id: str = "CLIENT-001", approved: bool = False) -> dict:
    data = DataLoader(DATA_DIR).load_all()
    profile = build_client_profile(client_id, data)
    risks = create_risk_alerts(profile)
    opportunities = identify_opportunities(profile)
    evidence = retrieve_supporting_evidence(profile, "risk opportunity working capital payment covenant")
    action = generate_next_best_action(risks, opportunities, evidence)
    brief = create_meeting_brief(profile, risks, opportunities, action)
    draft = draft_communication(profile, action)
    compliance = check_compliance(draft, evidence)
    status = "BLOCKED" if compliance["status"] != "PASS" else (approve(True) if approved else "PENDING")
    return {"client_id": client_id, "risks": risks, "opportunities": opportunities, "action": action, "brief": brief, "draft": draft, "compliance": compliance, "approval_status": status}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, default=str))
