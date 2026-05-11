from __future__ import annotations

import json

from backend.app_factory.prompts import ARCHITECTURE_SYSTEM_PROMPT
from backend.app_factory.schemas import ArchitectureSpec, RequirementsSpec
from backend.llm.groq_client import extract_groq_text, groq_chat_completion


def _fallback_architecture(requirements: RequirementsSpec) -> ArchitectureSpec:
    return ArchitectureSpec(
        components=[
            "App shell and page layout",
            "Item form",
            "Item list",
            "Summary panel",
            "Empty state",
        ],
        state_management="React useState with browser localStorage persistence.",
        folder_structure=[
            "app/page.tsx",
            "app/layout.tsx",
            "app/globals.css",
            "components/AppPanel.tsx",
            "lib/storage.ts",
            "tests/smoke.test.mjs",
        ],
        data_flow=[
            "User input updates React state.",
            "State is serialized to localStorage after changes.",
            "Derived summary values render from current state.",
        ],
        testing_strategy=[
            "Static smoke test checks required files.",
            "Production build validates TypeScript and Next.js compilation.",
        ],
        deployment_strategy=[
            "Build Docker image with npm run build.",
            "Run with npm start on Cloud Run port 8080.",
        ],
        limitations=[
            "Single-user browser demo only.",
            "Data stays in localStorage.",
            "No auth, backend database, or production integrations.",
        ],
    )


def generate_architecture(requirements: RequirementsSpec) -> ArchitectureSpec:
    try:
        response = groq_chat_completion(
            messages=[
                {"role": "system", "content": ARCHITECTURE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Return strict JSON only. Requirements: "
                        + requirements.model_dump_json()
                    ),
                },
            ],
            max_tokens=900,
            temperature=0.2,
        )
        data = json.loads(extract_groq_text(response))
        return ArchitectureSpec(**data)
    except Exception:
        return _fallback_architecture(requirements)

