"use client";

import { useEffect, useMemo, useState } from "react";
import { MessageResponse } from "@/components/ai-elements/message";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { DownloadIcon, SparklesIcon } from "lucide-react";

type AssignmentResult = {
  draft: string;
  critique: string;
  student_doubts: string;
  final: string;
  rubric: string;
  starter_code: string;
  topic: string;
  week: number | null;
  difficulty: string;
  refinement_notes?: string;
  syllabus_context: string;
};

type ResultTab = "assignment" | "rubric" | "starter" | "trace";

const generationSteps = [
  "Retrieving course context",
  "Checking syllabus support",
  "Drafting assignment",
  "Reviewing clarity and usability",
  "Finalizing rubric and starter material",
];

export default function AssignmentBuilderPage() {
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("Intermediate");
  const [refinementNotes, setRefinementNotes] = useState("");
  const [result, setResult] = useState<AssignmentResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<ResultTab>("assignment");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [completedInSeconds, setCompletedInSeconds] = useState<number | null>(
    null,
  );

  useEffect(() => {
    if (!loading) return;

    const startedAt = Date.now();
    setElapsedSeconds(0);
    setCurrentStepIndex(0);

    const timer = window.setInterval(() => {
      const seconds = Math.max(0, (Date.now() - startedAt) / 1000);
      setElapsedSeconds(seconds);
      setCurrentStepIndex((prev) => {
        const computed = Math.min(
          generationSteps.length - 1,
          Math.floor(seconds / 3),
        );
        return Math.max(prev, computed);
      });
    }, 250);

    return () => window.clearInterval(timer);
  }, [loading]);

  const summaryLine = useMemo(() => {
    if (!result) return "";

    const parts = [];
    if (result.week) parts.push(`Week ${result.week}`);
    parts.push(result.topic);
    parts.push(result.difficulty);
    if (completedInSeconds !== null) {
      parts.push(`Generated in ${completedInSeconds.toFixed(1)}s`);
    }
    return parts.join(" | ");
  }, [completedInSeconds, result]);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError("Enter a course topic first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setCompletedInSeconds(null);

    const startedAt = performance.now();

    try {
      const response = await fetch("/api/assignment-builder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.trim(),
          difficulty,
          refinement_notes: refinementNotes.trim(),
        }),
      });

      const payload = await response.json();

      if (!response.ok) {
        setError(payload.error ?? "Assignment generation failed.");
        return;
      }

      setResult(payload);
      setActiveTab("assignment");
      setCompletedInSeconds((performance.now() - startedAt) / 1000);
      setCurrentStepIndex(generationSteps.length - 1);
    } catch {
      setError("Could not reach the assignment builder service.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;

    const markdown = [
      `# Assignment: ${result.topic}`,
      "",
      `Difficulty: ${result.difficulty}`,
      result.week ? `Week: ${result.week}` : null,
      result.refinement_notes?.trim()
        ? `Faculty refinement notes: ${result.refinement_notes.trim()}`
        : null,
      "",
      "## Assignment",
      "",
      result.final,
      "",
      "## Grading Rubric",
      "",
      result.rubric,
      "",
      "## Starter Material",
      "",
      result.starter_code,
      "",
      "## Review Trace",
      "",
      "### Original Draft",
      "",
      result.draft,
      "",
      "### Professor Critique",
      "",
      result.critique,
      "",
      "### Student Doubts",
      "",
      result.student_doubts,
    ]
      .filter(Boolean)
      .join("\n");

    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const slug = result.topic.toLowerCase().replace(/[^a-z0-9]+/g, "-");
    link.href = url;
    link.download = `${slug || "assignment"}-pack.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const tabButton = (key: ResultTab, label: string) => (
    <button
      className={`rounded-full px-3 py-1.5 text-sm transition-colors ${
        activeTab === key
          ? "bg-foreground text-background"
          : "bg-card/40 text-muted-foreground hover:text-foreground"
      }`}
      onClick={() => setActiveTab(key)}
      type="button"
    >
      {label}
    </button>
  );

  return (
    <div className="min-h-dvh bg-background">
      <div className="mx-auto flex w-full max-w-5xl flex-col px-6 py-8">
        <div className="mb-6">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
            Faculty Workspace
          </p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight text-foreground">
            Assignment Builder
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
            Generate assignments only from CMSC389A syllabus and schedule
            material. Unsupported topics are refused instead of invented.
          </p>
        </div>

        <div className="rounded-3xl border border-border/40 bg-card/40 p-6 shadow-sm">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-border/30 pb-4">
            <div>
              <h2 className="text-lg font-medium text-foreground">
                Assignment Setup
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Start with a course-grounded topic, then generate a usable
                assignment pack.
              </p>
            </div>
            <div className="rounded-full border border-border/40 bg-background/60 px-3 py-1.5 text-xs text-muted-foreground">
              CMSC389A only
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-[1fr_220px]">
            <div className="space-y-2">
              <Label htmlFor="topic">Topic</Label>
              <Input
                id="topic"
                onChange={(event) => setTopic(event.target.value)}
                placeholder="MCP"
                value={topic}
              />
            </div>

            <div className="space-y-2">
              <Label>Difficulty</Label>
              <div className="flex flex-wrap gap-2">
                {["Beginner", "Intermediate", "Advanced"].map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setDifficulty(level)}
                    className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                      difficulty === level
                        ? "border-foreground bg-foreground text-background"
                        : "border-border/60 bg-card/40 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-5 space-y-2">
            <Label htmlFor="refinement-notes">Faculty refinement notes</Label>
            <Textarea
              id="refinement-notes"
              onChange={(event) => setRefinementNotes(event.target.value)}
              placeholder="Optional: emphasize implementation over theory, keep it doable in one week, require a small demo..."
              value={refinementNotes}
              className="min-h-[108px] resize-y rounded-2xl"
            />
          </div>

          <form
            className="mt-5 flex flex-wrap items-center gap-3"
            onSubmit={(event) => {
              event.preventDefault();
              void handleGenerate();
            }}
          >
            <button
              type="submit"
              className="inline-flex items-center rounded-xl bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading}
            >
              {loading ? "Generating..." : "Generate Assignment"}
            </button>
            <span className="text-sm text-muted-foreground">
              Generates only from retrieved course context
            </span>
          </form>

          {loading && (
            <div className="mt-5 rounded-2xl border border-border/40 bg-background/60 px-4 py-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                  <SparklesIcon className="size-4" />
                  {generationSteps[currentStepIndex]}
                </div>
                <div className="text-sm text-muted-foreground">
                  Elapsed: {elapsedSeconds.toFixed(1)}s
                </div>
              </div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-foreground/80 transition-all"
                  style={{
                    width: `${((currentStepIndex + 1) / generationSteps.length) * 100}%`,
                  }}
                />
              </div>
              <div className="mt-3 text-sm text-muted-foreground">
                Step {currentStepIndex + 1} of {generationSteps.length}
              </div>
            </div>
          )}

          {error && (
            <div className="mt-5 rounded-xl border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
              {error}
            </div>
          )}
        </div>

        {result && (
          <div className="mt-8">
            <div className="rounded-3xl border border-border/40 bg-card/30 p-5 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
                    Generated Output
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-foreground">
                    Assignment Pack
                  </h2>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {summaryLine}
                  </p>
                </div>
                <button
                  className="inline-flex h-9 items-center rounded-full border border-border/50 bg-background/60 px-4 text-sm text-foreground transition-colors hover:bg-card/60"
                  onClick={handleDownload}
                  type="button"
                >
                  <DownloadIcon className="mr-2 size-4" />
                  Download Markdown
                </button>
              </div>

              <div className="mt-5 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl border border-border/30 bg-background/50 px-4 py-3">
                  <div className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                    Topic
                  </div>
                  <div className="mt-1 text-sm font-medium text-foreground">
                    {result.topic}
                  </div>
                </div>
                <div className="rounded-2xl border border-border/30 bg-background/50 px-4 py-3">
                  <div className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                    Difficulty
                  </div>
                  <div className="mt-1 text-sm font-medium text-foreground">
                    {result.difficulty}
                  </div>
                </div>
                <div className="rounded-2xl border border-border/30 bg-background/50 px-4 py-3">
                  <div className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                    Turnaround
                  </div>
                  <div className="mt-1 text-sm font-medium text-foreground">
                    {completedInSeconds !== null
                      ? `${completedInSeconds.toFixed(1)}s`
                      : "Ready"}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-5">
              <h3 className="text-sm font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Pack Sections
              </h3>
            </div>

            <div className="mb-5 mt-3 flex flex-wrap gap-2">
              {tabButton("assignment", "Assignment")}
              {tabButton("rubric", "Rubric")}
              {tabButton("starter", "Starter Material")}
              {tabButton("trace", "Review Trace")}
            </div>

            <div className="rounded-3xl border border-border/40 bg-card/30 p-6 shadow-sm">
              {activeTab === "assignment" && (
                <>
                  <div className="mb-4">
                    <h3 className="text-lg font-medium text-foreground">
                      Assignment
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Main handout text for students.
                    </p>
                  </div>
                  <MessageResponse className="prose prose-invert prose-headings:tracking-tight prose-p:leading-7 prose-li:leading-7 max-w-none text-sm">
                    {result.final}
                  </MessageResponse>
                </>
              )}

              {activeTab === "rubric" && (
                <>
                  <div className="mb-4">
                    <h3 className="text-lg font-medium text-foreground">
                      Grading Rubric
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Five evaluation criteria tied to the assignment deliverables.
                    </p>
                  </div>
                  <MessageResponse className="prose prose-invert prose-headings:tracking-tight prose-p:leading-7 prose-li:leading-7 max-w-none text-sm">
                    {result.rubric}
                  </MessageResponse>
                </>
              )}

              {activeTab === "starter" && (
                <>
                  <div className="mb-4">
                    <h3 className="text-lg font-medium text-foreground">
                      Starter Material
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Minimal starting point or a note that no starter code is needed.
                    </p>
                  </div>
                  <MessageResponse className="prose prose-invert prose-headings:tracking-tight prose-p:leading-7 prose-li:leading-7 max-w-none text-sm">
                    {result.starter_code}
                  </MessageResponse>
                </>
              )}

              {activeTab === "trace" && (
                <div className="space-y-6 text-sm leading-7">
                  <div>
                    <h3 className="text-lg font-medium text-foreground">
                      Review Trace
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Internal generation trail to help faculty inspect how the pack was shaped.
                    </p>
                  </div>
                  <section>
                    <h3 className="mb-2 font-medium text-foreground">
                      Original Draft
                    </h3>
                    <MessageResponse className="prose prose-invert prose-p:leading-7 prose-li:leading-7 max-w-none text-sm text-muted-foreground">
                      {result.draft}
                    </MessageResponse>
                  </section>

                  <section>
                    <h3 className="mb-2 font-medium text-foreground">
                      Professor Critique
                    </h3>
                    <MessageResponse className="prose prose-invert prose-p:leading-7 prose-li:leading-7 max-w-none text-sm text-muted-foreground">
                      {result.critique}
                    </MessageResponse>
                  </section>

                  <section>
                    <h3 className="mb-2 font-medium text-foreground">
                      Student Doubts
                    </h3>
                    <MessageResponse className="prose prose-invert prose-p:leading-7 prose-li:leading-7 max-w-none text-sm text-muted-foreground">
                      {result.student_doubts}
                    </MessageResponse>
                  </section>

                  <section>
                    <h3 className="mb-2 font-medium text-foreground">
                      Course Context Used
                    </h3>
                    <MessageResponse className="prose prose-invert prose-p:leading-7 prose-li:leading-7 max-w-none text-sm text-muted-foreground">
                      {result.syllabus_context}
                    </MessageResponse>
                  </section>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
