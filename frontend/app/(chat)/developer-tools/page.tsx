"use client";

import { Loader2Icon, PlugZapIcon, WrenchIcon } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { cn } from "@/lib/utils";

type MCPTool = {
  name: string;
  description: string;
  inputSchema?: {
    properties?: Record<
      string,
      {
        type?: string;
        description?: string;
      }
    >;
    required?: string[];
  };
};

type ToolResponse = {
  result?: unknown;
  error?: string;
};

const defaultArgsByTool: Record<string, Record<string, unknown>> = {
  analyze_repo: { repo_path: "sample_repos/good_student" },
  get_review_history: { limit: 5 },
  ask_course_assistant: { question: "What topics are covered in Week 9?" },
};

function formatJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

export default function DeveloperToolsPage() {
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [selectedToolName, setSelectedToolName] = useState("analyze_repo");
  const [argumentsText, setArgumentsText] = useState(
    formatJson(defaultArgsByTool.analyze_repo),
  );
  const [connectionStatus, setConnectionStatus] = useState<
    "checking" | "connected" | "error"
  >("checking");
  const [loadingTools, setLoadingTools] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [responseText, setResponseText] = useState("");
  const [elapsedMs, setElapsedMs] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadTools() {
      setLoadingTools(true);
      setError("");
      try {
        const response = await fetch("/api/developer-tools", {
          cache: "no-store",
        });
        const payload = (await response.json()) as { tools?: MCPTool[]; error?: string };

        if (cancelled) return;

        if (!response.ok || !payload.tools) {
          setConnectionStatus("error");
          setError(payload.error ?? "Could not load MCP tools.");
          return;
        }

        setTools(payload.tools);
        setConnectionStatus("connected");

        if (payload.tools.length > 0) {
          const nextToolName = payload.tools.some(
            (tool) => tool.name === selectedToolName,
          )
            ? selectedToolName
            : payload.tools[0]!.name;
          setSelectedToolName(nextToolName);
          setArgumentsText(
            formatJson(defaultArgsByTool[nextToolName] ?? {}),
          );
        }
      } catch {
        if (cancelled) return;
        setConnectionStatus("error");
        setError("Could not reach the MCP tools backend.");
      } finally {
        if (!cancelled) setLoadingTools(false);
      }
    }

    void loadTools();

    return () => {
      cancelled = true;
    };
  }, [selectedToolName]);

  const selectedTool = useMemo(
    () => tools.find((tool) => tool.name === selectedToolName),
    [tools, selectedToolName],
  );

  const handleToolChange = (toolName: string) => {
    setSelectedToolName(toolName);
    setArgumentsText(formatJson(defaultArgsByTool[toolName] ?? {}));
    setError("");
    setResponseText("");
    setElapsedMs(null);
  };

  const runTool = async () => {
    setError("");
    setResponseText("");
    setElapsedMs(null);

    let parsedArguments: Record<string, unknown>;
    try {
      parsedArguments = argumentsText.trim()
        ? (JSON.parse(argumentsText) as Record<string, unknown>)
        : {};
    } catch {
      setError("Arguments must be valid JSON.");
      return;
    }

    setRunning(true);
    const startedAt = performance.now();

    try {
      const response = await fetch("/api/developer-tools", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: selectedToolName,
          arguments: parsedArguments,
        }),
      });

      const payload = (await response.json()) as ToolResponse;
      setElapsedMs(performance.now() - startedAt);

      if (!response.ok) {
        setError(payload.error ?? "MCP tool run failed.");
        return;
      }

      if (payload.error) {
        setError(payload.error);
        return;
      }

      setResponseText(formatJson(payload.result ?? {}));
    } catch {
      setElapsedMs(performance.now() - startedAt);
      setError("Could not run the selected MCP tool.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="min-h-dvh bg-background">
      <div className="mx-auto flex min-h-dvh w-full max-w-6xl flex-col px-6 py-8">
        <div className="mb-8">
          <div className="mb-3 text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">
            Developer Workspace
          </div>
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            MCP Console
          </h1>
          <p className="mt-3 max-w-3xl text-base leading-8 text-muted-foreground">
            Run the connected RepoMentor MCP tools from the UI, inspect their
            arguments, and verify the structured responses without leaving the
            app.
          </p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
          <section className="rounded-3xl border border-border/40 bg-card/30 p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-medium text-foreground">Connection</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Live view of the connected MCP tools.
                </p>
              </div>
              <div
                className={cn(
                  "rounded-full px-3 py-1 text-xs font-medium",
                  connectionStatus === "connected" &&
                    "bg-emerald-500/10 text-emerald-300",
                  connectionStatus === "checking" &&
                    "bg-amber-500/10 text-amber-300",
                  connectionStatus === "error" &&
                    "bg-destructive/10 text-destructive",
                )}
              >
                {connectionStatus === "connected"
                  ? "Connected"
                  : connectionStatus === "checking"
                    ? "Checking"
                    : "Error"}
              </div>
            </div>

            <div className="space-y-3">
              {loadingTools ? (
                <div className="rounded-2xl border border-border/30 bg-background/40 px-4 py-3 text-sm text-muted-foreground">
                  Loading MCP tools...
                </div>
              ) : (
                tools.map((tool) => (
                  <button
                    key={tool.name}
                    type="button"
                    onClick={() => handleToolChange(tool.name)}
                    className={cn(
                      "w-full rounded-2xl border px-4 py-3 text-left transition-colors",
                      selectedToolName === tool.name
                        ? "border-foreground/30 bg-foreground/5"
                        : "border-border/30 bg-background/40 hover:bg-card/50",
                    )}
                  >
                    <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                      <WrenchIcon className="size-4" />
                      {tool.name}
                    </div>
                    <div className="mt-2 text-sm leading-6 text-muted-foreground">
                      {tool.description}
                    </div>
                  </button>
                ))
              )}
            </div>
          </section>

          <section className="rounded-3xl border border-border/40 bg-card/30 p-5 shadow-sm">
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-medium text-foreground">Tool Runner</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Select a tool, adjust the JSON arguments if needed, and run it.
                </p>
              </div>
              {elapsedMs !== null ? (
                <div className="rounded-full border border-border/40 px-3 py-1 text-xs text-muted-foreground">
                  {`Completed in ${(elapsedMs / 1000).toFixed(1)}s`}
                </div>
              ) : null}
            </div>

            <div className="space-y-5">
              <div className="rounded-2xl border border-border/30 bg-background/40 p-4">
                <div className="text-sm font-medium text-foreground">
                  {selectedTool?.name ?? "Select a tool"}
                </div>
                <div className="mt-2 text-sm leading-6 text-muted-foreground">
                  {selectedTool?.description ??
                    "Pick a tool from the left to inspect and run it."}
                </div>
                {selectedTool?.inputSchema?.properties ? (
                  <div className="mt-4 space-y-2 text-sm text-muted-foreground">
                    {Object.entries(selectedTool.inputSchema.properties).map(
                      ([name, config]) => (
                        <div key={name} className="rounded-xl border border-border/20 px-3 py-2">
                          <span className="font-medium text-foreground">{name}</span>
                          {config.type ? ` · ${config.type}` : ""}
                          {config.description ? ` — ${config.description}` : ""}
                        </div>
                      ),
                    )}
                  </div>
                ) : null}
              </div>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-foreground">
                  JSON arguments
                </span>
                <textarea
                  value={argumentsText}
                  onChange={(event) => setArgumentsText(event.target.value)}
                  className="min-h-[180px] w-full rounded-2xl border border-border/40 bg-background/60 px-4 py-3 font-mono text-sm leading-7 text-foreground outline-none transition-colors focus:border-foreground/30"
                  spellCheck={false}
                />
              </label>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={() => void runTool()}
                  disabled={running || !selectedToolName}
                  className="inline-flex items-center gap-2 rounded-xl bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {running ? (
                    <Loader2Icon className="size-4 animate-spin" />
                  ) : (
                    <PlugZapIcon className="size-4" />
                  )}
                  {running ? "Running..." : "Run tool"}
                </button>
                <span className="text-sm text-muted-foreground">
                  Results stay local to this repo workspace.
                </span>
              </div>

              {error ? (
                <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  {error}
                </div>
              ) : null}

              <div className="rounded-2xl border border-border/30 bg-background/60 p-4">
                <div className="mb-3 text-sm font-medium text-foreground">
                  Response
                </div>
                <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap break-words rounded-xl border border-border/20 bg-card/20 p-4 font-mono text-sm leading-7 text-foreground">
                  {responseText || "{\n  \"result\": \"Run a tool to inspect the response.\"\n}"}
                </pre>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
