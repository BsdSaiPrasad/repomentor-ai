from __future__ import annotations

import json
import re

from backend.app_factory.prompts import REQUIREMENTS_SYSTEM_PROMPT
from backend.app_factory.schemas import RequirementsSpec, ScopeGuardResult
from backend.llm.groq_client import extract_groq_text, groq_chat_completion


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "generated-app"


def _guess_app_name(idea: str) -> str:
    lowered = idea.lower()
    for keyword, name in [
        ("flashcard", "Flashcard Trainer"),
        ("quiz", "Quiz Builder"),
        ("timer", "Focus Timer"),
        ("habit", "Habit Tracker"),
        ("expense", "Expense Tracker"),
        ("converter", "Unit Converter"),
        ("planner", "Study Planner"),
        ("note", "Notes Board"),
        ("todo", "Todo List"),
        ("to-do", "Todo List"),
        ("calculator", "Calculator"),
    ]:
        if keyword in lowered:
            return name
    return "Mini Web App"


def _fallback_requirements(idea: str, scope: ScopeGuardResult) -> RequirementsSpec:
    app_name = _guess_app_name(scope.reduced_scope or idea)
    return RequirementsSpec(
        app_name=app_name,
        app_slug=slugify(app_name),
        target_user="A student or instructor who needs a simple single-user productivity tool.",
        core_features=[
            "Create and manage simple items related to the app idea.",
            "Update item status or values directly in the browser.",
            "Show a clear summary of the current state.",
            "Persist data in browser localStorage for demo use.",
        ],
        non_goals=[
            "No authentication or user accounts.",
            "No payments or production integrations.",
            "No sensitive personal data storage.",
            "No backend database required for the generated demo app.",
        ],
        user_flow=[
            "User opens the app.",
            "User adds or edits an item.",
            "User reviews the updated state immediately.",
            "User can clear demo data when finished.",
        ],
        acceptance_criteria=[
            "App runs with npm run dev.",
            "App builds with npm run build.",
            "Primary workflow is usable on desktop and mobile.",
            "No secrets or credentials are included in source code.",
        ],
        data_model=[
            "Item: id, title, description, status, createdAt.",
        ],
        edge_cases=[
            "Empty input is rejected with inline feedback.",
            "Long labels wrap without breaking layout.",
            "localStorage failures do not crash the UI.",
        ],
    )


def generate_requirements(idea: str, scope: ScopeGuardResult) -> RequirementsSpec:
    base = scope.reduced_scope or idea
    try:
        response = groq_chat_completion(
            messages=[
                {"role": "system", "content": REQUIREMENTS_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Return strict JSON only for this app idea. "
                        f"Idea: {base}"
                    ),
                },
            ],
            max_tokens=900,
            temperature=0.2,
        )
        data = json.loads(extract_groq_text(response))
        data["app_slug"] = slugify(data.get("app_name", _guess_app_name(base)))
        return RequirementsSpec(**data)
    except Exception:
        return _fallback_requirements(idea, scope)

