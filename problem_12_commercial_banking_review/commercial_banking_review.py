"""Factuality-first monthly commercial banking client review.

Install dependencies:
    python -m pip install pandas requests python-dotenv

Configure an OpenRouter key in the repository .env file:
    OPENROUTER_API_KEY=your_key_here
    OPENROUTER_MODEL=openai/gpt-4o-mini

Run from the repository root:
    python .\problem_12_commercial_banking_review\commercial_banking_review.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

CLIENT_NAME = "Apex Manufacturing Pvt. Ltd."
REPORTING_PERIOD = "1 March 2026 to 31 March 2026"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"


def load_account_activity() -> pd.DataFrame:
    """Return one month of fictional account activity with a sensitive debit."""
    rows = [
        ["01 March 2026", "Customer deposit", "Invoice collection - Orion Motors", 1850000, "Credit", 6240000, 0, "Current account", "Completed"],
        ["03 March 2026", "Supplier payment", "Steel and components supplier", 920000, "Debit", 5320000, 0, "Current account", "Completed"],
        ["05 March 2026", "Payroll", "Monthly employee payroll", 1380000, "Debit", 3940000, 0, "Current account", "Completed"],
        ["08 March 2026", "Loan repayment", "Term loan instalment", 475000, "Debit", 3465000, 0, "Term loan", "Completed"],
        ["12 March 2026", "Customer deposit", "Export customer receipt", 2100000, "Credit", 5565000, 0, "Current account", "Completed"],
        ["15 March 2026", "Large debit", "Plant equipment purchase", 2800000, "Debit", 2765000, 0, "Current account", "Completed"],
        ["18 March 2026", "Bank fee", "Cash management service fee", 12500, "Debit", 2752500, 12500, "Cash management", "Completed"],
        ["21 March 2026", "Supplier payment", "Packaging materials", 640000, "Debit", 2112500, 0, "Current account", "Completed"],
        ["24 March 2026", "Customer payment", "Domestic customer settlement", 980000, "Credit", 3092500, 0, "Current account", "Completed"],
        ["27 March 2026", "Interest charge", "Working capital facility interest", 38500, "Debit", 3054000, 38500, "Working capital facility", "Completed"],
        ["31 March 2026", "Account balance", "Month-end closing balance", 3054000, "Credit", 3054000, 0, "Current account", "Completed"],
    ]
    columns = ["Date", "Transaction type", "Description", "Amount", "Debit/Credit", "Balance", "Fee", "Product", "Status"]
    return pd.DataFrame(rows, columns=columns)


def build_system_prompt() -> str:
    return f"""You are a Commercial Banking Relationship Manager communicating with {CLIENT_NAME}.
Review only the supplied monthly account activity. Factual accuracy is more important than sounding persuasive or polished.
Use ONLY facts, figures, dates, transactions, products, and events explicitly present in the input. Never invent amounts, dates, descriptions, products, fees, reasons, performance, intentions, risk events, or recommendations.
Write exactly two paragraphs and no bullets. Do not reproduce the entire statement. Mention sensitive items carefully. If an explanation is unavailable, say that the information is not available rather than guessing.
Do not recommend trades, promise investment returns, invent next-best-product recommendations, or make unsupported claims about financial health. Do not add general banking facts or any information absent from the input."""


def build_user_prompt(activity: pd.DataFrame) -> str:
    return f"""Client name: {CLIENT_NAME}
Reporting period: {REPORTING_PERIOD}

Monthly account activity:
{activity.to_csv(index=False)}

Generate exactly two paragraphs using only the information provided above. If information is missing, explicitly state that it is not available. Do not infer or estimate any amount, date, reason, product, or event."""


def call_llm(system_prompt: str, user_prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to the .env file.")
    model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
    payload = {"model": model, "temperature": 0.0, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except (requests.RequestException, ValueError, IndexError, KeyError, TypeError) as exc:
        raise RuntimeError(f"LLM request failed or returned an invalid response: {exc}") from exc
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("The LLM returned an empty response.")
    return content.strip()


def validate_two_paragraphs(review: str) -> tuple[bool, list[str]]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", review) if part.strip()]
    warnings = []
    if len(paragraphs) != 2:
        warnings.append(f"Expected exactly 2 paragraphs, found {len(paragraphs)}.")
    if re.search(r"^\s*[-*•]\s+", review, re.MULTILINE):
        warnings.append("Bullet points were detected.")
    return len(paragraphs) == 2 and not warnings, warnings


def normalize_amount(value: str) -> int | None:
    digits = re.sub(r"[^0-9]", "", value)
    return int(digits) if digits else None


def extract_facts(review: str) -> dict[str, list[str]]:
    amounts = re.findall(r"(?:₹|Rs\.?\s*)\s*[\d,]+|\b\d{1,3}(?:,\d{2,3})+(?:\.\d+)?\b", review, re.IGNORECASE)
    dates = re.findall(r"\b(?:\d{1,2}\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b|\b\d{1,2}\s+March\s+2026\b", review, re.IGNORECASE)
    events = ["large debit", "loan repayment", "bank fee", "customer deposit", "customer payment", "supplier payment", "payroll", "interest charge", "balance reduction"]
    found_events = [event for event in events if event in review.lower()]
    return {"amounts": amounts, "dates": dates, "events": found_events}


def fact_check(review: str, activity: pd.DataFrame) -> list[dict[str, str]]:
    facts = extract_facts(review)
    source_amounts = {int(value) for value in activity["Amount"].tolist() + activity["Fee"].tolist() + activity["Balance"].tolist()}
    source_dates = {str(date).lower() for date in activity["Date"]}
    source_events = {str(event).lower() for event in activity["Transaction type"]}
    results = []
    for item in facts["amounts"]:
        amount = normalize_amount(item)
        results.append({"Item": item, "Type": "Amount", "Status": "IN SOURCE" if amount in source_amounts else "NOT IN SOURCE"})
    for item in facts["dates"]:
        results.append({"Item": item, "Type": "Date", "Status": "IN SOURCE" if item.lower() in source_dates else "NOT IN SOURCE"})
    for item in facts["events"]:
        supported = item in source_events or (item == "balance reduction" and activity["Balance"].iloc[-1] < activity["Balance"].iloc[0])
        results.append({"Item": item, "Type": "Event", "Status": "IN SOURCE" if supported else "NOT IN SOURCE"})
    return results


def check_for_prohibited_content(review: str) -> list[str]:
    patterns = [r"\b(recommend|recommendation)\b.*\btrade\b", r"\bguarantee(?:d|s)?\b.*\breturn", r"next[- ]best product", r"investment return"]
    return [pattern for pattern in patterns if re.search(pattern, review, re.IGNORECASE)]


def make_send_decision(paragraphs_ok: bool, fact_results: list[dict[str, str]], prohibited: list[str]) -> bool:
    return paragraphs_ok and not any(item["Status"] == "NOT IN SOURCE" for item in fact_results) and not prohibited


def main() -> int:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    activity = load_account_activity()
    print(f"Loaded {len(activity)} account activity records for {CLIENT_NAME}.")
    try:
        review = call_llm(build_system_prompt(), build_user_prompt(activity))
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1

    paragraphs_ok, warnings = validate_two_paragraphs(review)
    print("\n" + "=" * 40 + "\nCLIENT REVIEW\n" + "=" * 40 + "\n")
    print(review)
    if warnings:
        print("\nWarnings: " + " ".join(warnings))

    fact_results = fact_check(review, activity)
    prohibited = check_for_prohibited_content(review)
    print("\n" + "=" * 40 + "\nFACT CHECK\n" + "=" * 40)
    if fact_results:
        for item in fact_results:
            print(f"\nItem: {item['Item']}\nType: {item['Type']}\nStatus: {item['Status']}")
    else:
        print("\nNo extractable amounts, dates, or named events found.")
    print("\nNote: This is a basic validation mechanism, not a complete guarantee against hallucinations.")

    decision = make_send_decision(paragraphs_ok, fact_results, prohibited)
    print("\n" + "=" * 40 + "\nSEND-AS-IS DECISION\n" + "=" * 40)
    print(f"\nFACT CHECK RESULT: {'PASS' if not any(item['Status'] == 'NOT IN SOURCE' for item in fact_results) else 'FAIL'}")
    print(f"PARAGRAPH COUNT: {'PASS' if paragraphs_ok else 'FAIL'}")
    print(f"\nDecision: {'YES — The draft can be sent as-is.' if decision else 'NO — The draft requires review because unsupported information or formatting issues were detected.'}")
    return 0 if decision else 2


if __name__ == "__main__":
    sys.exit(main())
