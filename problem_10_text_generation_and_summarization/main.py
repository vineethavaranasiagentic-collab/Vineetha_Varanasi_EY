"""Interactive, privacy-conscious customer email AI terminal application."""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from openrouter_client import OpenRouterError, complete_chat
from prompts import build_messages


# Load the .env file located beside this script, regardless of the terminal's
# current directory. The file is ignored by Git and its values are never printed.
load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)


def read_multiline_email():
    """Read a multi-line email and keep it only in temporary memory."""
    print("Paste the customer email below.")
    print("Type END on a new line when finished:")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def print_section(title, value):
    # Print one result category with a consistent, easy-to-read heading.
    print("\n" + "=" * 40)
    print(f" {title}")
    print("=" * 40)
    if isinstance(value, list):
        if value:
            for number, item in enumerate(value, start=1):
                print(f"{number}. {item}")
        else:
            print("None identified.")
    else:
        print(value if value else "Not provided.")


def main():
    # Ask for the task and email details interactively; nothing is saved.
    print("=" * 40)
    print(" Customer Email AI Assistant")
    print("=" * 40)
    print("\nWhat do you need?")
    user_instruction = input("> ").strip()
    if not user_instruction:
        print("Error: Please enter what you need.")
        return 1

    print("\nCustomer Email ID:")
    email_id = input("> ").strip()
    if not email_id:
        print("Error: Customer Email ID cannot be empty.")
        return 1

    print("\nCustomer Email Subject (optional):")
    subject = input("> ").strip() or None
    body = read_multiline_email()
    if not body:
        print("Error: Customer email body cannot be empty.")
        return 1

    try:
        result = complete_chat(build_messages(user_instruction, email_id, subject, body))
    except OpenRouterError as exc:
        print(f"\nError: {exc}")
        return 1

    # Parse only the current response; no email data is written or retained.
    try:
        analysis = json.loads(result)
    except json.JSONDecodeError:
        print("\nError: The AI service returned an invalid JSON response.")
        return 1

    print_section("EMAIL ID", email_id)
    fields = [
        ("EMAIL SUMMARY", "summary"),
        ("CUSTOMER INTENT", "intent"),
        ("KEY POINTS", "key_points"),
        ("ACTION ITEMS", "action_items"),
        ("SENTIMENT", "sentiment"),
        ("URGENCY", "urgency"),
        ("MISSING INFORMATION", "missing_information"),
        ("RISK/REVIEW FLAGS", "risk_flags"),
        ("DRAFT CUSTOMER REPLY", "draft_reply"),
    ]
    for title, key in fields:
        print_section(title, analysis.get(key))

    print("\nProcessing complete. No customer data was saved by this application.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
