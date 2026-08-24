from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


class DataLoader:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def load(self, filename: str) -> list[dict[str, Any]]:
        with (self.data_dir / filename).open(newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def load_all(self) -> dict[str, list[dict[str, Any]]]:
        return {
            name.removesuffix(".csv"): self.load(name)
            for name in (
                "clients.csv", "financials.csv", "transactions.csv",
                "products.csv", "covenants.csv", "crm_notes.csv",
                "industry_news.csv",
            )
        }
