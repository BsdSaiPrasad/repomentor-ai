import os
import time
from dotenv import load_dotenv
from backend.llm.groq_client import (
    extract_groq_text,
    extract_groq_usage,
    groq_chat_completion,
)

load_dotenv()


def call_llm(system: str, user: str, model: str = "llama-3.1-8b-instant") -> dict:
    """Call Groq LLM and return response + metadata."""
    start = time.time()
    response = groq_chat_completion(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
        max_tokens=1500,
    )
    duration = round(time.time() - start, 2)
    content = extract_groq_text(response)
    usage = extract_groq_usage(response)
    return {
        "text": content,
        "duration": duration,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "total_tokens": usage["total_tokens"],
        "model": model,
    }
