from pathlib import Path

from backend.app_factory import code_agent, orchestrator
from backend.app_factory.schemas import AgentRunResult


def test_orchestrator_scope_and_plan_path():
    session = orchestrator.start_scope("Build a simple study planner")
    planned = orchestrator.plan_app(session.session_id)

    assert planned.scope is not None
    assert planned.requirements is not None
    assert planned.architecture is not None
    assert planned.stage == "planned"


def test_code_generation_writes_expected_files(tmp_path, monkeypatch):
    monkeypatch.setattr(code_agent, "GENERATED_ROOT", tmp_path)
    monkeypatch.setattr(
        orchestrator,
        "run_tests",
        lambda app_path: AgentRunResult(status="skipped", summary="Skipped in unit test."),
    )
    monkeypatch.setattr(
        orchestrator,
        "run_security_scan",
        lambda app_path: AgentRunResult(status="passed", summary="No findings."),
    )

    session = orchestrator.start_scope("Build a quiz app")
    orchestrator.plan_app(session.session_id)
    generated = orchestrator.generate_code(session.session_id, approved=True)

    assert generated.app_path is not None
    app_path = Path(generated.app_path)
    assert (app_path / "app" / "page.tsx").exists()
    assert (app_path / "Dockerfile").exists()
    assert (app_path / "README.md").exists()
    assert generated.stage == "generated"
