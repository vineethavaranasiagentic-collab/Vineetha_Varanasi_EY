from __future__ import annotations

from typing import Any

from rules.risk_rules import detect_risks


def create_risk_alerts(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return detect_risks(profile)
