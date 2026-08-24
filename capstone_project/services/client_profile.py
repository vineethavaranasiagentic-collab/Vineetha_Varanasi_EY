from __future__ import annotations

from typing import Any


def build_client_profile(client_id: str, data: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    profile: dict[str, Any] = {}
    for key, rows in data.items():
        matches = [row for row in rows if row.get("client_id") == client_id]
        if key == "clients":
            profile["client"] = matches[0] if matches else {}
        elif key == "industry_news":
            industry = profile.get("client", {}).get("industry")
            profile[key] = [row for row in rows if row.get("industry") == industry]
        else:
            profile[key] = matches
    return profile
