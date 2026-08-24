from __future__ import annotations

import re
from typing import Any


BLOCKED_PHRASES = ("guaranteed", "risk-free", "will definitely", "no risk")


def check_compliance(draft: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    lowered = draft.lower()
    unsupported = [phrase for phrase in BLOCKED_PHRASES if phrase in lowered]
    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", draft)
    evidence_text = " ".join(str(item) for item in evidence)
    if numbers and not any(number in evidence_text for number in numbers):
        unsupported.append("numeric claim without matching evidence")
    return {"status": "BLOCKED" if unsupported else "PASS", "issues": unsupported}
