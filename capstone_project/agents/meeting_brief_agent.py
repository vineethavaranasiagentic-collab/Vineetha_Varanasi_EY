from __future__ import annotations

from typing import Any


def create_meeting_brief(profile: dict[str, Any], risks: list[dict[str, Any]], opportunities: list[dict[str, Any]], action: dict[str, Any]) -> dict[str, Any]:
    return {
        "client": profile.get("client", {}),
        "financials": profile.get("financials", []),
        "risks": risks,
        "opportunities": opportunities,
        "next_best_action": action,
        "talking_points": ["Review recent account activity", "Discuss identified risks and opportunities", "Agree on next steps"],
    }
