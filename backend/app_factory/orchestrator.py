from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from backend.app_factory.architecture_agent import generate_architecture
from backend.app_factory.code_agent import generate_app_files
from backend.app_factory.deploy_agent import deploy_generated_app
from backend.app_factory.docs_agent import write_docs
from backend.app_factory.github_agent import write_github_actions_stub
from backend.app_factory.requirements_agent import generate_requirements
from backend.app_factory.schemas import AppFactorySession
from backend.app_factory.scope_guard import evaluate_scope
from backend.app_factory.security_agent import run_security_scan
from backend.app_factory.testing_agent import run_tests


SESSIONS: dict[str, AppFactorySession] = {}


def _approval(kind: str) -> dict[str, str]:
    return {
        "kind": kind,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "storage": "in-memory",
    }


def start_scope(idea: str) -> AppFactorySession:
    session = AppFactorySession(session_id=str(uuid.uuid4()), idea=idea)
    session.scope = evaluate_scope(idea)
    session.stage = "scoped"
    SESSIONS[session.session_id] = session
    return session


def get_session(session_id: str) -> AppFactorySession:
    if session_id not in SESSIONS:
        raise ValueError("Unknown App Factory session.")
    return SESSIONS[session_id]


def plan_app(session_id: str) -> AppFactorySession:
    session = get_session(session_id)
    if not session.scope:
        raise ValueError("Run scope guard before planning.")
    if not session.scope.allowed and not session.scope.reduced_scope:
        raise ValueError("Scope guard rejected this app idea.")

    session.requirements = generate_requirements(session.idea, session.scope)
    session.architecture = generate_architecture(session.requirements)
    session.app_slug = session.requirements.app_slug
    session.stage = "planned"
    return session


def generate_code(session_id: str, approved: bool) -> AppFactorySession:
    session = get_session(session_id)
    if not approved:
        raise ValueError("Human approval is required before code generation.")
    if not session.requirements or not session.architecture:
        raise ValueError("Requirements and architecture are required before code generation.")

    session.approvals.append(_approval("code_generation"))
    session.stage = "code_approved"

    app_path, generated_files = generate_app_files(session.requirements, session.architecture)
    docs_result = write_docs(app_path, session.requirements, session.architecture)
    write_github_actions_stub(app_path, session.requirements.app_slug)
    test_result = run_tests(app_path)
    security_result = run_security_scan(app_path)

    session.app_path = str(app_path)
    session.generated_files = generated_files
    session.documentation = docs_result
    session.testing = test_result
    session.security = security_result
    session.stage = "generated"
    return session


def deploy_app(
    session_id: str,
    approved: bool,
    project_id: str | None = None,
    region: str | None = None,
    repository: str | None = None,
) -> AppFactorySession:
    session = get_session(session_id)
    if not approved:
        raise ValueError("Human approval is required before deployment.")
    if not session.app_path or not session.app_slug:
        raise ValueError("Generate the app before deployment.")

    session.approvals.append(_approval("deployment"))
    session.stage = "deployment_approved"
    result = deploy_generated_app(
        app_path=Path(session.app_path),
        app_slug=session.app_slug,
        project_id=project_id,
        region=region,
        repository=repository,
    )
    session.deployment = result
    if result.status == "passed":
        session.stage = "deployed"
        marker = "deployed to "
        if marker in result.summary:
            session.deployed_url = result.summary.split(marker, 1)[1].strip()
    return session

