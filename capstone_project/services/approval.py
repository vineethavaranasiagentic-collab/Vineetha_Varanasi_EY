from __future__ import annotations


def approve(approved: bool) -> str:
    return "READY_TO_SEND" if approved else "STOP"
