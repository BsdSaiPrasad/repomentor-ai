import os
import time
from typing import Any

import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def groq_chat_completion(
    *,
    messages: list[dict[str, str]],
    model: str = "llama-3.1-8b-instant",
    max_tokens: int = 512,
    temperature: float | None = None,
) -> dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if temperature is not None:
        payload["temperature"] = temperature

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )
            if response.status_code == 429 and attempt < 2:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else float(2 ** (attempt + 1))
                time.sleep(delay)
                continue
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code in {429, 500, 502, 503, 504} and attempt < 2:
                retry_after = (
                    exc.response.headers.get("Retry-After")
                    if exc.response is not None
                    else None
                )
                delay = float(retry_after) if retry_after else float(2 ** (attempt + 1))
                time.sleep(delay)
                last_error = exc
                continue
            raise
        except requests.RequestException as exc:
            if attempt < 2:
                time.sleep(float(2 ** (attempt + 1)))
                last_error = exc
                continue
            raise

    if last_error is not None:
        raise last_error
    raise RuntimeError("Groq request failed without a response.")


def extract_groq_text(response: dict[str, Any]) -> str:
    return response["choices"][0]["message"]["content"]


def extract_groq_usage(response: dict[str, Any]) -> dict[str, int]:
    usage = response.get("usage", {})
    return {
        "prompt_tokens": int(usage.get("prompt_tokens", 0)),
        "completion_tokens": int(usage.get("completion_tokens", 0)),
        "total_tokens": int(usage.get("total_tokens", 0)),
    }
