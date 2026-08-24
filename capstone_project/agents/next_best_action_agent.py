from __future__ import annotations

from typing import Any


def generate_next_best_action(risks: list[dict[str, Any]], opportunities: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    if risks:
        risk = risks[0]
        return {"action": "Schedule a risk review with the client", "reason": risk["risk"], "priority": risk["priority"], "evidence": evidence, "confidence": 0.85}
    if opportunities:
        opportunity = opportunities[0]
        return {"action": f"Discuss {opportunity['opportunity']}", "reason": opportunity["reason"], "priority": "MEDIUM", "evidence": evidence, "confidence": 0.80}
    return {"action": "Continue routine relationship monitoring", "reason": "No priority signal detected", "priority": "LOW", "evidence": evidence, "confidence": 0.60}
