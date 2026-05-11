from __future__ import annotations

from pathlib import Path


def write_github_actions_stub(app_path: Path, app_slug: str) -> str:
    workflow_dir = app_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    path = workflow_dir / "deploy-cloud-run.yml"
    path.write_text(
        f"""name: Deploy {app_slug} to Cloud Run

on:
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Placeholder
        run: echo "Configure Workload Identity and Cloud Run deployment for {app_slug}."
""",
        encoding="utf-8",
    )
    return str(path)

