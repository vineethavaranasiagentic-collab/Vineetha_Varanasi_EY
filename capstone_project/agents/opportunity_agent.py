from __future__ import annotations

from typing import Any

from rules.opportunity_rules import detect_opportunities


def identify_opportunities(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return detect_opportunities(profile)
