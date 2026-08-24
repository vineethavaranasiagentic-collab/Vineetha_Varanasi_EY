"""Interactive document-based customer email summarizer and reply drafter."""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from document_reader import DocumentReadError, extract_email_text
from models import EmailAnalysis
from openrouter_client import OpenRouterError, complete_chat
from prompts import build_messages


# Load .env beside this script; customer documents are never written by the app.
load_dotenv(Path(__file__).with_name(".env"), override=False)


def print_section(title, value):
    """Print one result section in a format that is easy for a beginner to read."""
    print("\n" + "=" * 40)
    print(f" {title}")
    print("=" * 40)
    if isinstance(value, list):
        if value:
            for number, item in enumerate(value, 1):
                print(f"{number}. {item}")
        else:
            print("None identified.")
    else:
        print(value or "Not provided.")


def main():
    """Read one document, call OpenRouter, validate, and display its results."""
    print("=" * 40)
    print(" Customer Email AI Assistant")
    print("=" * 40)
    file_name = input("\nEnter the path of the customer email document:\n> ").strip()
    if not file_name:
        print("Error: Please enter a document path.")
        return 1

    try:
        document_text = extract_email_text(file_name)
    except DocumentReadError as exc:
        print(f"Error: {exc}")
        return 1

    print("\nDocument loaded successfully.")
    print("\nWhat would you like to do?\n")
    print("1. Summarize the customer email")
    print("2. Draft a customer reply")
    print("3. Summarize the email and draft a reply")
    choice = input("\nEnter your choice:\n> ").strip()
    if choice not in {"1", "2", "3"}:
        print("Error: Please choose 1, 2, or 3.")
        return 1

    print("\nProcessing document...\nAnalyzing customer email...\nGenerating response...")
    try:
        raw_response = complete_chat(build_messages(choice, document_text))
        analysis = EmailAnalysis.model_validate(json.loads(raw_response))
    except OpenRouterError as exc:
        print(f"Error: {exc}")
        return 1
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        print("Error: The AI service returned an invalid structured response.")
        return 1

    print_section("EMAIL SUMMARY", analysis.summary)
    print_section("CUSTOMER INTENT", analysis.intent)
    print_section("KEY POINTS", analysis.key_points)
    print_section("ACTION ITEMS", analysis.action_items)
    print_section("MISSING INFORMATION", analysis.missing_information)
    print_section("DRAFT CUSTOMER REPLY", analysis.draft_reply)
    print("\nThe reply is a draft only. No email was sent and no document was modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
