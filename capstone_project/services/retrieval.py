from __future__ import annotations

import re
from typing import Any


def retrieve_evidence(profile: dict[str, Any], query: str, limit: int = 5) -> list[dict[str, Any]]:
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    candidates: list[dict[str, Any]] = []
    for category, rows in profile.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            text = " ".join(str(value) for value in row.values())
            score = sum(term in text.lower() for term in terms)
            if score:
                candidates.append({"category": category, "score": score, "record": row})
    return sorted(candidates, key=lambda item: item["score"], reverse=True)[:limit]
