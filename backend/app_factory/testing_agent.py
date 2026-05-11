from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from backend.app_factory.schemas import AgentRunResult


def _run(command: list[str], cwd: Path, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def run_tests(app_path: Path) -> AgentRunResult:
    if shutil.which("npm") is None:
        return AgentRunResult(
            status="skipped",
            summary="npm is not available in this runtime. Generated files were created, but build tests were skipped.",
        )

    stdout_parts: list[str] = []
    stderr_parts: list[str] = []

    if not (app_path / "node_modules").exists():
        install = _run(["npm", "install"], app_path, timeout=300)
        stdout_parts.append(install.stdout)
        stderr_parts.append(install.stderr)
        if install.returncode != 0:
            return AgentRunResult(
                status="failed",
                summary="npm install failed.",
                stdout="\n".join(stdout_parts),
                stderr="\n".join(stderr_parts),
            )

    smoke = _run(["npm", "test"], app_path, timeout=120)
    stdout_parts.append(smoke.stdout)
    stderr_parts.append(smoke.stderr)
    if smoke.returncode != 0:
        return AgentRunResult(
            status="failed",
            summary="Smoke tests failed.",
            stdout="\n".join(stdout_parts),
            stderr="\n".join(stderr_parts),
        )

    build = _run(["npm", "run", "build"], app_path, timeout=300)
    stdout_parts.append(build.stdout)
    stderr_parts.append(build.stderr)
    if build.returncode != 0:
        return AgentRunResult(
            status="failed",
            summary="Next.js production build failed.",
            stdout="\n".join(stdout_parts),
            stderr="\n".join(stderr_parts),
        )

    return AgentRunResult(
        status="passed",
        summary="npm install, smoke test, and production build completed.",
        stdout="\n".join(stdout_parts),
        stderr="\n".join(stderr_parts),
    )

