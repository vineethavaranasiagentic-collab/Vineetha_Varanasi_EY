from __future__ import annotations

from typing import Any

from services.retrieval import retrieve_evidence


def retrieve_supporting_evidence(profile: dict[str, Any], query: str) -> list[dict[str, Any]]:
    return retrieve_evidence(profile, query)
