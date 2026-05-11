from __future__ import annotations

from pathlib import Path

from backend.app_factory.gcp_cloud_run import deploy_to_cloud_run
from backend.app_factory.schemas import AgentRunResult


def deploy_generated_app(
    *,
    app_path: Path,
    app_slug: str,
    project_id: str | None = None,
    region: str | None = None,
    repository: str | None = None,
) -> AgentRunResult:
    return deploy_to_cloud_run(
        app_path=app_path,
        app_slug=app_slug,
        project_id=project_id,
        region=region,
        repository=repository,
    )

