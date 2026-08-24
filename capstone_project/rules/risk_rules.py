from __future__ import annotations

from typing import Any


def detect_risks(profile: dict[str, Any]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for row in profile.get("transactions", []):
        if row.get("transaction_type", "").lower() in {"delayed_payment", "failed_payment"}:
            risks.append({"risk": "Payment risk", "priority": "HIGH" if row["transaction_type"].lower() == "failed_payment" else "MEDIUM", "evidence": row})
    for row in profile.get("covenants", []):
        if row.get("status", "").lower() in {"warning", "breach"}:
            risks.append({"risk": "Covenant stress", "priority": "HIGH", "evidence": row})
    for row in profile.get("industry_news", []):
        if row.get("risk_indicator", "").lower() in {"high", "negative", "deteriorating"}:
            risks.append({"risk": "Industry risk", "priority": "MEDIUM", "evidence": row})
    return risks
