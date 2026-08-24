"""OpenRouter Chat Completions client with safe error handling."""

import os
import time

import httpx


# Model is intentionally defined in code rather than read from the environment.
# Use the exact OpenRouter model slug supported by the account/provider.
OPENROUTER_MODEL = "openai/gpt-5.6-luna"


class OpenRouterError(Exception):
    """Friendly error raised for configuration, network, or API failures."""


def complete_chat(messages):
    """Send one request without logging or persisting email data or secrets."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")

    if not api_key:
        raise OpenRouterError("OPENROUTER_API_KEY is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    # Retry temporary failures, but never retry authentication failures.
    for attempt in range(3):
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            if attempt == 2:
                raise OpenRouterError("The OpenRouter request timed out.") from exc
            time.sleep(2**attempt)
            continue
        except httpx.RequestError as exc:
            if attempt == 2:
                raise OpenRouterError("Unable to connect to OpenRouter.") from exc
            time.sleep(2**attempt)
            continue

        if response.status_code in (401, 403):
            raise OpenRouterError("OpenRouter authentication failed.")
        if response.status_code == 429:
            if attempt == 2:
                raise OpenRouterError("OpenRouter rate limit reached. Try again later.")
            time.sleep(2**attempt)
            continue
        if response.status_code >= 500:
            if attempt == 2:
                raise OpenRouterError("OpenRouter is temporarily unavailable.")
            time.sleep(2**attempt)
            continue
        if response.status_code >= 400:
            raise OpenRouterError("OpenRouter rejected the request.")

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError("OpenRouter returned an invalid response.") from exc

    raise OpenRouterError("The OpenRouter request failed.")
