from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from backend.app_factory.schemas import AgentRunResult


def deploy_to_cloud_run(
    *,
    app_path: Path,
    app_slug: str,
    project_id: str | None = None,
    region: str | None = None,
    repository: str | None = None,
) -> AgentRunResult:
    project_id = project_id or os.getenv("GCP_PROJECT_ID")
    region = region or os.getenv("GCP_REGION")
    repository = repository or os.getenv("GCP_ARTIFACT_REPOSITORY")

    missing = [
        name
        for name, value in [
            ("GCP_PROJECT_ID", project_id),
            ("GCP_REGION", region),
            ("GCP_ARTIFACT_REPOSITORY", repository),
        ]
        if not value
    ]
    if missing:
        return AgentRunResult(
            status="failed",
            summary="Missing deployment environment variables: " + ", ".join(missing),
        )
    if shutil.which("gcloud") is None:
        return AgentRunResult(
            status="failed",
            summary="gcloud is not installed or not available on PATH.",
        )

    image = f"{region}-docker.pkg.dev/{project_id}/{repository}/{app_slug}"
    build = subprocess.run(
        ["gcloud", "builds", "submit", "--tag", image],
        cwd=app_path,
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    if build.returncode != 0:
        return AgentRunResult(
            status="failed",
            summary="Cloud Build failed for generated app.",
            stdout=build.stdout,
            stderr=build.stderr,
        )

    deploy = subprocess.run(
        [
            "gcloud",
            "run",
            "deploy",
            app_slug,
            "--image",
            image,
            "--platform",
            "managed",
            "--region",
            region,
            "--allow-unauthenticated",
            "--format",
            "value(status.url)",
        ],
        cwd=app_path,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if deploy.returncode != 0:
        return AgentRunResult(
            status="failed",
            summary="Cloud Run deploy failed for generated app.",
            stdout=deploy.stdout,
            stderr=deploy.stderr,
        )

    return AgentRunResult(
        status="passed",
        summary=f"Generated app deployed to {deploy.stdout.strip()}",
        stdout=deploy.stdout,
        stderr=deploy.stderr,
    )

