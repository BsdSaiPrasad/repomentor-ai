from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from backend.app_factory.schemas import AgentRunResult


SECRET_PATTERNS = [
    r"(?i)api[_-]?key\s*=\s*['\"][^'\"]+",
    r"(?i)secret\s*=\s*['\"][^'\"]+",
    r"(?i)password\s*=\s*['\"][^'\"]+",
    r"AIza[0-9A-Za-z\-_]{35}",
    r"sk-[0-9A-Za-z\-_]{20,}",
]

DANGEROUS_PATTERNS = [
    "dangerouslySetInnerHTML",
    "eval(",
    "new Function(",
    "document.cookie",
    "localStorage.setItem(\"password\"",
]


def _text_files(app_path: Path) -> list[Path]:
    ignored = {"node_modules", ".next", ".git"}
    files: list[Path] = []
    for path in app_path.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file() and path.suffix in {".ts", ".tsx", ".js", ".mjs", ".json", ".md", ".css"}:
            files.append(path)
    return files


def run_security_scan(app_path: Path) -> AgentRunResult:
    findings: list[str] = []

    for path in _text_files(app_path):
        content = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(app_path)
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, content):
                findings.append(f"Potential secret-like value in {relative}")
        for pattern in DANGEROUS_PATTERNS:
            if pattern in content:
                findings.append(f"Dangerous pattern `{pattern}` in {relative}")

    audit_output = ""
    audit_error = ""
    if shutil.which("npm") and (app_path / "package-lock.json").exists():
        audit = subprocess.run(
            ["npm", "audit", "--audit-level=high"],
            cwd=app_path,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        audit_output = audit.stdout
        audit_error = audit.stderr
        if audit.returncode not in {0, 1}:
            findings.append("npm audit could not complete cleanly.")

    report_path = app_path / "security_report.md"
    report = [
        "# Security Report",
        "",
        "## Findings",
        "",
        *(f"- {finding}" for finding in findings),
        "" if findings else "- No high-confidence local security findings.",
        "",
        "## npm audit",
        "",
        "npm audit runs only when package-lock.json exists.",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")

    return AgentRunResult(
        status="failed" if findings else "passed",
        summary=(
            f"{len(findings)} security finding(s) detected."
            if findings
            else "No high-confidence local security findings detected."
        ),
        stdout=audit_output,
        stderr=audit_error,
        report_path=str(report_path),
    )

