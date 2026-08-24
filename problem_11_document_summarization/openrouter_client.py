"""Small OpenRouter client with safe, friendly error messages."""

import os
import time

import httpx


MODEL = "openai/gpt-5.6-luna"


class OpenRouterError(Exception):
    """Raised when the AI service cannot complete the request."""


def complete_chat(messages):
    """Send one in-memory request; never print or save secrets or email text."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    if not api_key:
        raise OpenRouterError("OPENROUTER_API_KEY is not configured.")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    for attempt in range(3):
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            if attempt == 2:
                raise OpenRouterError("The request timed out.") from exc
            time.sleep(2 ** attempt)
            continue
        except httpx.RequestError as exc:
            if attempt == 2:
                raise OpenRouterError("Unable to connect to the AI service.") from exc
            time.sleep(2 ** attempt)
            continue

        if response.status_code in (401, 403):
            raise OpenRouterError("OpenRouter authentication failed.")
        if response.status_code == 429:
            if attempt == 2:
                raise OpenRouterError("Rate limit reached. Try again later.")
            time.sleep(2 ** attempt)
            continue
        if response.status_code >= 500:
            if attempt == 2:
                raise OpenRouterError("The AI service is temporarily unavailable.")
            time.sleep(2 ** attempt)
            continue
        if response.status_code >= 400:
            raise OpenRouterError("The AI service rejected the request.")

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError("The AI service returned an invalid response.") from exc

    raise OpenRouterError("The AI request failed.")
