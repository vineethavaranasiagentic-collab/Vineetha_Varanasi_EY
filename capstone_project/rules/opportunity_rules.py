from __future__ import annotations

from typing import Any


def detect_opportunities(profile: dict[str, Any]) -> list[dict[str, Any]]:
    products = {row.get("product_name", "").lower() for row in profile.get("products", [])}
    transactions = profile.get("transactions", [])
    opportunities: list[dict[str, Any]] = []
    if len(transactions) >= 2 and "working capital facility" not in products:
        opportunities.append({"opportunity": "Working Capital Facility", "score": 75, "reason": "Active transaction history and no working-capital product."})
    if "cash management" not in products and len(transactions) >= 2:
        opportunities.append({"opportunity": "Cash Management", "score": 70, "reason": "Meaningful transaction activity and no cash-management product."})
    return opportunities
