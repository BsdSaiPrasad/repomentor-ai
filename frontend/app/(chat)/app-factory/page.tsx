"use client";

import {
  CheckCircle2Icon,
  CloudUploadIcon,
  FileCode2Icon,
  Loader2Icon,
  ShieldCheckIcon,
  SparklesIcon,
  XCircleIcon,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type AgentRunResult = {
  status: "passed" | "failed" | "skipped";
  summary: string;
  stdout?: string;
  stderr?: string;
  report_path?: string | null;
};

type AppFactorySession = {
  session_id: string;
  idea: string;
  stage: string;
  scope?: {
    allowed: boolean;
    complexity_score: number;
    risk_level: "low" | "medium" | "high";
    reason: string;
    reduced_scope?: string | null;
    requires_human_approval: boolean;
  } | null;
  requirements?: {
    app_name: string;
    app_slug: string;
    target_user: string;
    core_features: string[];
    non_goals: string[];
    user_flow: string[];
    acceptance_criteria: string[];
    data_model: string[];
    edge_cases: string[];
  } | null;
  architecture?: {
    framework: string;
    language: string;
    router: string;
    components: string[];
    state_management: string;
    folder_structure: string[];
    data_flow: string[];
    testing_strategy: string[];
    deployment_strategy: string[];
    limitations: string[];
  } | null;
  app_slug?: string | null;
  app_path?: string | null;
  generated_files: Array<{ path: string; description: string }>;
  testing?: AgentRunResult | null;
  security?: AgentRunResult | null;
  documentation?: AgentRunResult | null;
  deployment?: AgentRunResult | null;
  deployed_url?: string | null;
};

const examples = [
  "A flashcard app for studying CMSC389A terms",
  "A habit tracker for daily coding practice",
  "A quiz app for prompt engineering concepts",
  "A study planner with tasks and deadlines",
];

function StatusPill({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  return (
    <span
      className={cn(
        "rounded-full border px-2.5 py-1 text-xs font-medium",
        normalized === "passed" && "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
        normalized === "failed" && "border-red-500/30 bg-red-500/10 text-red-300",
        normalized === "skipped" && "border-amber-500/30 bg-amber-500/10 text-amber-300",
        !["passed", "failed", "skipped"].includes(normalized) &&
          "border-border/50 bg-card/50 text-muted-foreground",
      )}
    >
      {status}
    </span>
  );
}

function ListBlock({ title, items }: { title: string; items?: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h3 className="mb-2 text-sm font-medium text-foreground">{title}</h3>
      <ul className="space-y-2 text-sm text-muted-foreground">
        {items.map((item) => (
          <li className="rounded-lg border border-border/30 bg-background/40 px-3 py-2" key={item}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function AppFactoryPage() {
  const [idea, setIdea] = useState("");
  const [session, setSession] = useState<AppFactorySession | null>(null);
  const [error, setError] = useState("");
  const [loadingAction, setLoadingAction] = useState("");
  const [gcpProjectId, setGcpProjectId] = useState("");
  const [gcpRegion, setGcpRegion] = useState("us-central1");
  const [gcpRepository, setGcpRepository] = useState("cloud-run-source-deploy");

  const canPlan = Boolean(session?.scope);
  const canGenerate = Boolean(session?.requirements && session.architecture);
  const canDeploy = Boolean(session?.app_path);

  const currentStep = useMemo(() => {
    if (session?.deployed_url) return "Deployed";
    if (session?.app_path) return "Generated";
    if (session?.architecture) return "Awaiting code approval";
    if (session?.scope) return "Scoped";
    return "New";
  }, [session]);

  const callFactory = async (body: Record<string, unknown>, actionLabel: string) => {
    setLoadingAction(actionLabel);
    setError("");
    try {
      const response = await fetch("/api/app-factory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const payload = (await response.json()) as {
        session?: AppFactorySession;
        error?: string;
      };

      if (!response.ok || !payload.session) {
        setError(payload.error ?? "App Factory request failed.");
        return;
      }

      setSession(payload.session);
    } catch {
      setError("Could not reach App Factory.");
    } finally {
      setLoadingAction("");
    }
  };

  return (
    <div className="min-h-dvh bg-background">
      <div className="mx-auto flex w-full max-w-6xl flex-col px-6 py-8">
        <div className="mb-7">
          <p className="text-xs font-medium uppercase tracking-[0.22em] text-muted-foreground">
            Agentic Build Workspace
          </p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight text-foreground">
            App Factory
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
            Turn a safe small-app idea into a generated Next.js project through
            scoped planning, human approvals, testing, security checks, docs, and
            Cloud Run deployment readiness.
          </p>
        </div>

        <section className="rounded-3xl border border-border/40 bg-card/40 p-6 shadow-sm">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-border/30 pb-4">
            <div>
              <h2 className="text-lg font-medium text-foreground">App Idea</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Keep it small, single-user, and safe. App Factory will reduce or
                reject risky requests.
              </p>
            </div>
            <StatusPill status={currentStep} />
          </div>

          <Label htmlFor="idea">Natural language prompt</Label>
          <Textarea
            id="idea"
            className="mt-2 min-h-[130px] resize-y rounded-2xl"
            onChange={(event) => setIdea(event.target.value)}
            placeholder="Example: Build a flashcard app for studying prompt engineering terms."
            value={idea}
          />

          <div className="mt-4 flex flex-wrap gap-2">
            {examples.map((example) => (
              <button
                className="rounded-full border border-border/40 bg-background/40 px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
                key={example}
                onClick={() => setIdea(example)}
                type="button"
              >
                {example}
              </button>
            ))}
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              className="inline-flex items-center gap-2 rounded-xl bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:opacity-60"
              disabled={!idea.trim() || Boolean(loadingAction)}
              onClick={() => callFactory({ action: "scope", idea }, "scope")}
              type="button"
            >
              {loadingAction === "scope" ? (
                <Loader2Icon className="size-4 animate-spin" />
              ) : (
                <SparklesIcon className="size-4" />
              )}
              Run Scope Guard
            </button>
            <span className="text-sm text-muted-foreground">
              Human approval is required before code and deployment.
            </span>
          </div>
          {error ? (
            <div className="mt-4 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          ) : null}
        </section>

        {session?.scope ? (
          <section className="mt-6 rounded-3xl border border-border/40 bg-card/30 p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-medium text-foreground">Scope Guard Result</h2>
              <div className="flex gap-2">
                <StatusPill status={session.scope.allowed ? "allowed" : "rejected"} />
                <StatusPill status={`risk: ${session.scope.risk_level}`} />
                <StatusPill status={`complexity: ${session.scope.complexity_score}`} />
              </div>
            </div>
            <p className="text-sm leading-6 text-muted-foreground">{session.scope.reason}</p>
            {session.scope.reduced_scope ? (
              <div className="mt-4 rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
                Reduced scope: {session.scope.reduced_scope}
              </div>
            ) : null}
            <button
              className="mt-5 rounded-xl border border-border/60 bg-background/60 px-4 py-2 text-sm font-medium text-foreground disabled:opacity-60"
              disabled={!canPlan || Boolean(loadingAction)}
              onClick={() =>
                callFactory(
                  { action: "plan", session_id: session.session_id },
                  "plan",
                )
              }
              type="button"
            >
              {loadingAction === "plan" ? "Planning..." : "Generate Requirements + Architecture"}
            </button>
          </section>
        ) : null}

        {session?.requirements && session.architecture ? (
          <section className="mt-6 grid gap-6 xl:grid-cols-2">
            <div className="rounded-3xl border border-border/40 bg-card/30 p-6">
              <h2 className="text-lg font-medium text-foreground">Requirements</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                {session.requirements.app_name} / {session.requirements.app_slug}
              </p>
              <div className="mt-5 space-y-5">
                <ListBlock title="Core Features" items={session.requirements.core_features} />
                <ListBlock title="Acceptance Criteria" items={session.requirements.acceptance_criteria} />
                <ListBlock title="Non-goals" items={session.requirements.non_goals} />
              </div>
            </div>

            <div className="rounded-3xl border border-border/40 bg-card/30 p-6">
              <h2 className="text-lg font-medium text-foreground">Architecture</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                {session.architecture.framework} / {session.architecture.language} /{" "}
                {session.architecture.router}
              </p>
              <div className="mt-5 space-y-5">
                <ListBlock title="Components" items={session.architecture.components} />
                <ListBlock title="Folder Structure" items={session.architecture.folder_structure} />
                <ListBlock title="Limitations" items={session.architecture.limitations} />
              </div>
            </div>

            <div className="rounded-3xl border border-border/40 bg-card/30 p-6 xl:col-span-2">
              <h2 className="text-lg font-medium text-foreground">
                Human Approval Checkpoint
              </h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Approving this step writes a complete Next.js app into
                generated_apps/{session.requirements.app_slug}.
              </p>
              <button
                className="mt-5 inline-flex items-center gap-2 rounded-xl bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:opacity-60"
                disabled={!canGenerate || Boolean(loadingAction)}
                onClick={() =>
                  callFactory(
                    {
                      action: "generate",
                      session_id: session.session_id,
                      approve_code_generation: true,
                    },
                    "generate",
                  )
                }
                type="button"
              >
                {loadingAction === "generate" ? (
                  <Loader2Icon className="size-4 animate-spin" />
                ) : (
                  <FileCode2Icon className="size-4" />
                )}
                Approve + Generate Code
              </button>
            </div>
          </section>
        ) : null}

        {session?.app_path ? (
          <section className="mt-6 rounded-3xl border border-border/40 bg-card/30 p-6">
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-medium text-foreground">Generated App</h2>
                <p className="mt-1 text-sm text-muted-foreground">{session.app_path}</p>
              </div>
              <StatusPill status={session.stage} />
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-border/40 bg-background/40 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <CheckCircle2Icon className="size-4 text-emerald-300" />
                  <h3 className="text-sm font-medium">Testing</h3>
                </div>
                <StatusPill status={session.testing?.status ?? "pending"} />
                <p className="mt-3 text-sm text-muted-foreground">
                  {session.testing?.summary ?? "Not run yet."}
                </p>
              </div>

              <div className="rounded-2xl border border-border/40 bg-background/40 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <ShieldCheckIcon className="size-4 text-sky-300" />
                  <h3 className="text-sm font-medium">Security</h3>
                </div>
                <StatusPill status={session.security?.status ?? "pending"} />
                <p className="mt-3 text-sm text-muted-foreground">
                  {session.security?.summary ?? "Not run yet."}
                </p>
              </div>

              <div className="rounded-2xl border border-border/40 bg-background/40 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <FileCode2Icon className="size-4 text-violet-300" />
                  <h3 className="text-sm font-medium">Documentation</h3>
                </div>
                <StatusPill status={session.documentation?.status ?? "pending"} />
                <p className="mt-3 text-sm text-muted-foreground">
                  {session.documentation?.summary ?? "Not run yet."}
                </p>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="mb-3 text-sm font-medium text-foreground">Generated Files</h3>
              <div className="grid gap-2 md:grid-cols-2">
                {session.generated_files.map((file) => (
                  <div
                    className="rounded-lg border border-border/30 bg-background/40 px-3 py-2 text-sm text-muted-foreground"
                    key={file.path}
                  >
                    {file.path}
                  </div>
                ))}
              </div>
            </div>
          </section>
        ) : null}

        {session?.app_path ? (
          <section className="mt-6 rounded-3xl border border-border/40 bg-card/30 p-6">
            <div className="mb-5 flex items-center gap-2">
              <CloudUploadIcon className="size-5 text-muted-foreground" />
              <h2 className="text-lg font-medium text-foreground">Deployment Approval</h2>
            </div>
            <p className="text-sm text-muted-foreground">
              Deployment uses gcloud and Cloud Run. Leave fields blank to use
              backend environment variables.
            </p>
            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <input
                className="rounded-xl border border-border/50 bg-background/60 px-3 py-2 text-sm"
                onChange={(event) => setGcpProjectId(event.target.value)}
                placeholder="GCP project ID"
                value={gcpProjectId}
              />
              <input
                className="rounded-xl border border-border/50 bg-background/60 px-3 py-2 text-sm"
                onChange={(event) => setGcpRegion(event.target.value)}
                placeholder="GCP region"
                value={gcpRegion}
              />
              <input
                className="rounded-xl border border-border/50 bg-background/60 px-3 py-2 text-sm"
                onChange={(event) => setGcpRepository(event.target.value)}
                placeholder="Artifact repository"
                value={gcpRepository}
              />
            </div>
            <button
              className="mt-5 inline-flex items-center gap-2 rounded-xl bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:opacity-60"
              disabled={!canDeploy || Boolean(loadingAction)}
              onClick={() =>
                callFactory(
                  {
                    action: "deploy",
                    session_id: session.session_id,
                    approve_deployment: true,
                    gcp_project_id: gcpProjectId || undefined,
                    gcp_region: gcpRegion || undefined,
                    gcp_artifact_repository: gcpRepository || undefined,
                  },
                  "deploy",
                )
              }
              type="button"
            >
              {loadingAction === "deploy" ? (
                <Loader2Icon className="size-4 animate-spin" />
              ) : (
                <CloudUploadIcon className="size-4" />
              )}
              Approve + Deploy
            </button>

            {session.deployment ? (
              <div className="mt-5 rounded-2xl border border-border/40 bg-background/40 p-4">
                <div className="flex items-center gap-2">
                  {session.deployment.status === "passed" ? (
                    <CheckCircle2Icon className="size-4 text-emerald-300" />
                  ) : (
                    <XCircleIcon className="size-4 text-red-300" />
                  )}
                  <StatusPill status={session.deployment.status} />
                </div>
                <p className="mt-3 text-sm text-muted-foreground">
                  {session.deployment.summary}
                </p>
                {session.deployed_url ? (
                  <a
                    className="mt-3 inline-block text-sm text-emerald-300 underline"
                    href={session.deployed_url}
                    rel="noreferrer"
                    target="_blank"
                  >
                    {session.deployed_url}
                  </a>
                ) : null}
              </div>
            ) : null}
          </section>
        ) : null}
      </div>
    </div>
  );
}
