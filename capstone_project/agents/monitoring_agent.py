from __future__ import annotations

from typing import Any


def monitor(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "transaction_count": len(profile.get("transactions", [])),
        "product_count": len(profile.get("products", [])),
        "covenant_count": len(profile.get("covenants", [])),
        "industry_news_count": len(profile.get("industry_news", [])),
    }
