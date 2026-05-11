from __future__ import annotations

import re

from backend.app_factory.schemas import ScopeGuardResult


BLOCKED_PATTERNS = {
    "auth": r"\b(auth|login|signup|sign up|oauth|password|roles?)\b",
    "payments": r"\b(payment|stripe|paypal|checkout|subscription|billing)\b",
    "banking": r"\b(bank|banking|loan|credit score|investment|trading|crypto)\b",
    "medical": r"\b(medical|doctor|diagnosis|therapy|patient|prescription)\b",
    "legal": r"\b(legal|lawyer|lawsuit|contract review)\b",
    "marketplace": r"\b(marketplace|multi-vendor|seller|buyer platform)\b",
    "realtime": r"\b(real[- ]?time chat|websocket|multiplayer|live chat)\b",
    "sensitive": r"\b(ssn|social security|passport|health record|tax return)\b",
}

SAFE_APP_HINTS = {
    "calculator",
    "todo",
    "to-do",
    "notes",
    "flashcards",
    "quiz",
    "timer",
    "habit",
    "expense",
    "converter",
    "planner",
    "tracker",
}


def evaluate_scope(idea: str) -> ScopeGuardResult:
    normalized = idea.strip().lower()
    if not normalized:
        return ScopeGuardResult(
            allowed=False,
            complexity_score=1,
            risk_level="low",
            reason="No app idea was provided.",
            reduced_scope="Provide a small single-user app idea such as a timer, quiz, or notes app.",
        )

    hits = [
        name
        for name, pattern in BLOCKED_PATTERNS.items()
        if re.search(pattern, normalized)
    ]
    word_count = len(normalized.split())
    complexity = 2
    if word_count > 35:
        complexity += 1
    if any(term in normalized for term in ["dashboard", "analytics", "admin", "database"]):
        complexity += 1
    if hits:
        complexity = max(complexity, 5 if len(hits) > 1 else 4)

    if hits:
        return ScopeGuardResult(
            allowed=False,
            complexity_score=min(complexity, 5),
            risk_level="high" if len(hits) > 1 else "medium",
            reason=(
                "The idea includes restricted production concerns: "
                + ", ".join(sorted(hits))
                + "."
            ),
            reduced_scope=(
                "A single-page mock demo showing the main workflow without auth, "
                "payments, sensitive data, real-time systems, or production integrations."
            ),
        )

    safe_match = any(hint in normalized for hint in SAFE_APP_HINTS)
    return ScopeGuardResult(
        allowed=True,
        complexity_score=min(complexity if not safe_match else 2, 5),
        risk_level="low" if complexity <= 2 else "medium",
        reason="Small single-user app idea with no restricted production requirements.",
        reduced_scope=None,
    )

