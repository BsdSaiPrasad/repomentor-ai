from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]
FactoryStage = Literal[
    "new",
    "scoped",
    "planned",
    "code_approved",
    "generated",
    "deployment_approved",
    "deployed",
]


class ScopeGuardResult(BaseModel):
    allowed: bool
    complexity_score: int = Field(ge=1, le=5)
    risk_level: RiskLevel
    reason: str
    reduced_scope: str | None = None
    requires_human_approval: bool = True


class RequirementsSpec(BaseModel):
    app_name: str
    app_slug: str
    target_user: str
    core_features: list[str]
    non_goals: list[str]
    user_flow: list[str]
    acceptance_criteria: list[str]
    data_model: list[str]
    edge_cases: list[str]


class ArchitectureSpec(BaseModel):
    framework: str = "Next.js"
    language: str = "TypeScript"
    router: str = "App Router"
    components: list[str]
    state_management: str
    folder_structure: list[str]
    data_flow: list[str]
    testing_strategy: list[str]
    deployment_strategy: list[str]
    limitations: list[str]


class GeneratedFile(BaseModel):
    path: str
    description: str


class AgentRunResult(BaseModel):
    status: Literal["passed", "failed", "skipped"]
    summary: str
    stdout: str = ""
    stderr: str = ""
    report_path: str | None = None


class AppFactorySession(BaseModel):
    session_id: str
    idea: str
    stage: FactoryStage = "new"
    scope: ScopeGuardResult | None = None
    requirements: RequirementsSpec | None = None
    architecture: ArchitectureSpec | None = None
    app_slug: str | None = None
    app_path: str | None = None
    generated_files: list[GeneratedFile] = []
    testing: AgentRunResult | None = None
    security: AgentRunResult | None = None
    documentation: AgentRunResult | None = None
    deployment: AgentRunResult | None = None
    deployed_url: str | None = None
    approvals: list[dict[str, Any]] = []


class AppFactoryRequest(BaseModel):
    action: Literal["scope", "plan", "generate", "deploy", "status"]
    idea: str | None = None
    session_id: str | None = None
    approve_code_generation: bool = False
    approve_deployment: bool = False
    gcp_project_id: str | None = None
    gcp_region: str | None = None
    gcp_artifact_repository: str | None = None


class AppFactoryResponse(BaseModel):
    session: AppFactorySession
    error: str | None = None

