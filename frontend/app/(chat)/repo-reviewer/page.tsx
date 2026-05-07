"use client";

import { useMemo, useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SearchIcon, ShieldAlertIcon } from "lucide-react";

type ReviewIssue = {
  agent: string;
  severity: string;
  location: string;
  issue: string;
  fix: string;
};

type AgentBreakdown = {
  agent: string;
  score: number;
  summary: string;
  issues: ReviewIssue[];
  duration?: number;
};

type ReviewResult = {
  overall_score: number;
  grade: string;
  breakdown: AgentBreakdown[];
  all_issues: ReviewIssue[];
  agent_count: number;
};

const severityTone: Record<string, string> = {
  High: "border-red-500/30 bg-red-500/10 text-red-100",
  Medium: "border-amber-500/30 bg-amber-500/10 text-amber-100",
  Low: "border-sky-500/30 bg-sky-500/10 text-sky-100",
  Potential: "border-zinc-500/30 bg-zinc-500/10 text-zinc-100",
};

export default function RepoReviewerPage() {
  const [repoPath, setRepoPath] = useState("");
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const groupedIssues = useMemo(() => {
    if (!result) return [];
    return result.all_issues.slice(0, 6);
  }, [result]);

  const handleAnalyze = async () => {
    if (!repoPath.trim()) {
      setError("Enter a local repo path or GitHub URL first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/repo-review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_path: repoPath.trim() }),
      });

      const payload = await response.json();

      if (!response.ok) {
        setError(payload.error ?? "Repo review failed.");
        return;
      }

      setResult(payload as ReviewResult);
    } catch {
      setError("Could not reach the repo review backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-dvh bg-background">
      <div className="mx-auto flex w-full max-w-6xl flex-col px-6 py-8">
        <div className="mb-6">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
            Review Workspace
          </p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight text-foreground">
            Repo Reviewer
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
            Review a local Python repo or GitHub URL and get concise findings
            with location and fix suggestions.
          </p>
        </div>

        <div className="rounded-3xl border border-border/40 bg-card/40 p-6 shadow-sm">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-border/30 pb-4">
            <div>
              <h2 className="text-lg font-medium text-foreground">
                Analysis Input
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Paste a local repo path or GitHub repository URL.
              </p>
            </div>
            <div className="rounded-full border border-border/40 bg-background/60 px-3 py-1.5 text-xs text-muted-foreground">
              Python repos only
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="repo-path">Repo path or GitHub URL</Label>
            <Input
              id="repo-path"
              value={repoPath}
              onChange={(event) => setRepoPath(event.target.value)}
              placeholder="sample_repos/good_student or https://github.com/..."
            />
          </div>

          <form
            className="mt-5 flex flex-wrap items-center gap-3"
            onSubmit={(event) => {
              event.preventDefault();
              void handleAnalyze();
            }}
          >
            <button
              type="submit"
              className="inline-flex items-center rounded-xl bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading}
            >
              <SearchIcon className="mr-2 size-4" />
              {loading ? "Analyzing..." : "Analyze Repo"}
            </button>
            <span className="text-sm text-muted-foreground">
              Code quality, security, and documentation
            </span>
          </form>

          {error && (
            <div className="mt-5 rounded-xl border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
              {error}
            </div>
          )}
        </div>

        {result && (
          <div className="mt-8 space-y-5">
            <div className="rounded-3xl border border-border/40 bg-card/30 p-5 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
                    Review Summary
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-foreground">
                    {result.grade}
                  </h2>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {repoPath}
                  </p>
                </div>
              </div>

              <div className="mt-5 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl border border-border/30 bg-background/50 px-4 py-3">
                  <div className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                    Overall Score
                  </div>
                  <div className="mt-1 text-sm font-medium text-foreground">
                    {result.overall_score}/100
                  </div>
                </div>
                <div className="rounded-2xl border border-border/30 bg-background/50 px-4 py-3">
                  <div className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                    Agents
                  </div>
                  <div className="mt-1 text-sm font-medium text-foreground">
                    {result.agent_count}
                  </div>
                </div>
                <div className="rounded-2xl border border-border/30 bg-background/50 px-4 py-3">
                  <div className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                    Findings Shown
                  </div>
                  <div className="mt-1 text-sm font-medium text-foreground">
                    {groupedIssues.length}
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-border/40 bg-card/30 p-5 shadow-sm">
              <h3 className="text-lg font-medium text-foreground">
                Key Findings
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Highest-signal issues with location and fix guidance.
              </p>

              <div className="mt-5 space-y-3">
                {groupedIssues.map((issue, index) => (
                  <div
                    key={`${issue.agent}-${issue.location}-${index}`}
                    className={`rounded-2xl border px-4 py-4 ${severityTone[issue.severity] ?? "border-border/30 bg-background/50 text-foreground"}`}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full border border-current/20 px-2 py-0.5 text-[11px] uppercase tracking-[0.14em]">
                        {issue.severity}
                      </span>
                      <span className="text-xs text-current/70">
                        {issue.agent}
                      </span>
                    </div>
                    <div className="mt-3 text-sm font-medium text-current">
                      {issue.issue}
                    </div>
                    <div className="mt-2 text-xs text-current/70">
                      Where: {issue.location || "Not specified"}
                    </div>
                    <div className="mt-2 text-sm text-current/90">
                      Fix: {issue.fix}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-border/40 bg-card/30 p-5 shadow-sm">
              <h3 className="text-lg font-medium text-foreground">
                Agent Breakdown
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Per-agent score and concise summary.
              </p>

              <div className="mt-5 grid gap-3 md:grid-cols-3">
                {result.breakdown.map((agent) => (
                  <div
                    key={agent.agent}
                    className="rounded-2xl border border-border/30 bg-background/50 px-4 py-4"
                  >
                    <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                      <ShieldAlertIcon className="size-4" />
                      {agent.agent}
                    </div>
                    <div className="mt-3 text-2xl font-semibold text-foreground">
                      {agent.score}/100
                    </div>
                    <p className="mt-3 text-sm leading-6 text-muted-foreground">
                      {agent.summary}
                    </p>
                    {typeof agent.duration === "number" && (
                      <div className="mt-3 text-xs text-muted-foreground">
                        Completed in {agent.duration.toFixed(1)}s
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
