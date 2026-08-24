from __future__ import annotations

from typing import Any


def draft_communication(profile: dict[str, Any], action: dict[str, Any]) -> str:
    company = profile.get("client", {}).get("company_name", "the client")
    return f"Subject: Relationship discussion\n\nDear {company} team,\n\nI would like to schedule a conversation to discuss {action['action'].lower()}.\n\nRegards,\nRelationship Manager"
