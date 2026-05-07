"use client";

import { SendIcon, SparklesIcon } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type CourseChatMessage = {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
};

const suggestions = [
  "What topics are covered in Week 9?",
  "What is MCP in this course?",
  "What assignment is released in Week 3?",
  "Can you explain prompt engineering more simply?",
];

export function CourseAssistantPage() {
  const [messages, setMessages] = useState<CourseChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const lastAssistantSources = useMemo(() => {
    for (let index = messages.length - 1; index >= 0; index -= 1) {
      if (messages[index]?.role === "assistant" && messages[index]?.sources) {
        return messages[index].sources ?? [];
      }
    }
    return [];
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  const sendQuestion = async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    const nextMessages: CourseChatMessage[] = [
      ...messages,
      { role: "user", content: trimmed },
    ];

    setMessages(nextMessages);
    setInput("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/course-assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: trimmed,
          messages: nextMessages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        }),
      });

      const payload = await response.json();

      if (!response.ok) {
        setError(payload.error ?? "Course assistant failed.");
        return;
      }

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            typeof payload.answer === "string"
              ? payload.answer
              : "I couldn't generate an answer.",
          sources: Array.isArray(payload.sources) ? payload.sources : [],
        },
      ]);
    } catch {
      setError("Could not reach the course assistant service.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    await sendQuestion(input);
  };

  return (
    <div className="min-h-dvh bg-background">
      <div className="mx-auto flex h-dvh w-full max-w-5xl flex-col px-6 py-6">
        <div className="shrink-0 pb-4">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Course Assistant
          </h1>
        </div>

        <div className="flex min-h-0 flex-1 flex-col">
          <div className="min-h-0 flex-1 overflow-y-auto pr-1">
            {messages.length === 0 ? (
              <div className="flex min-h-full items-center justify-center pb-6">
                <div className="w-full max-w-3xl text-center">
                  <h2 className="text-5xl font-semibold tracking-tight text-foreground">
                    Ask about CMSC389A
                  </h2>
                  <p className="mx-auto mt-4 max-w-2xl text-base leading-8 text-muted-foreground">
                    Ask about weekly topics, assignments, deadlines, or course
                    concepts. Every answer stays grounded in the CMSC389A
                    course materials.
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-4 pb-6">
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}-${message.content.slice(0, 16)}`}
                    className={cn(
                      "max-w-3xl rounded-3xl border px-5 py-4 text-sm leading-7 shadow-sm",
                      message.role === "user"
                        ? "ml-auto border-border/40 bg-card/60 text-foreground"
                        : "border-border/30 bg-card/30 text-foreground",
                    )}
                  >
                    <div className="mb-1 text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
                      {message.role === "user" ? "You" : "Course Assistant"}
                    </div>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    {message.role === "assistant" &&
                      (message.sources?.length ?? 0) > 0 && (
                        <details className="mt-3 rounded-2xl border border-border/40 bg-background/60 px-3 py-2">
                          <summary className="cursor-pointer text-xs text-muted-foreground">
                            Sources used
                          </summary>
                          <ul className="mt-2 space-y-2 text-xs leading-6 text-muted-foreground">
                            {message.sources?.map((source, sourceIndex) => (
                              <li key={`${sourceIndex}-${source.slice(0, 24)}`}>
                                {source}
                              </li>
                            ))}
                          </ul>
                        </details>
                      )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <form
            className="sticky bottom-0 mt-auto border-t border-border/20 bg-background/95 pb-2 pt-4 backdrop-blur"
            onSubmit={(event) => {
              event.preventDefault();
              void handleSubmit();
            }}
          >
            <div className="mx-auto w-full max-w-4xl space-y-4">
              {messages.length === 0 && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                    <SparklesIcon className="size-4" />
                    Try one of these
                  </div>
                  <div className="grid gap-3 md:grid-cols-2">
                    {suggestions.map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        onClick={() => void sendQuestion(suggestion)}
                        disabled={loading}
                        className="rounded-2xl border border-border/40 bg-card/20 px-4 py-3 text-left text-sm text-muted-foreground transition-colors hover:bg-card/50 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <div className="rounded-3xl border border-border/40 bg-card/30 p-4 shadow-sm">
                <Textarea
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey &&
                      !loading &&
                      input.trim()
                    ) {
                      event.preventDefault();
                      void handleSubmit();
                    }
                  }}
                  placeholder="Ask about syllabus topics, assignments, or course concepts..."
                  className="min-h-[120px] resize-y border-0 bg-transparent px-1 text-sm leading-7 shadow-none focus-visible:ring-0"
                />
                <div className="mt-3 flex flex-wrap items-center justify-between gap-3 border-t border-border/20 pt-3">
                  <span className="text-xs text-muted-foreground">
                    {loading
                      ? "Looking through the course materials..."
                      : messages.length > 0
                        ? `${messages.length} messages in this chat`
                        : "Grounded in CMSC389A course materials only"}
                  </span>
                  <div className="flex items-center gap-2">
                    {messages.length > 0 && (
                      <button
                        type="button"
                        className="rounded-xl border border-border/50 bg-card/30 px-4 py-2 text-sm text-foreground transition-colors hover:bg-card/60 disabled:cursor-not-allowed disabled:opacity-60"
                        onClick={() => {
                          setMessages([]);
                          setInput("");
                          setError("");
                        }}
                        disabled={loading}
                      >
                        Clear chat
                      </button>
                    )}
                    <button
                      type="submit"
                      className="inline-flex items-center gap-2 rounded-xl bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                      disabled={loading || !input.trim()}
                    >
                      <SendIcon className="size-4" />
                      {loading ? "Sending..." : "Send"}
                    </button>
                  </div>
                </div>
              </div>
              {error ? (
                <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  {error}
                </div>
              ) : null}
              {!loading &&
              messages.length > 0 &&
              lastAssistantSources.length === 0 ? (
                <div className="text-xs text-muted-foreground">
                  No source snippets were returned for the latest answer.
                </div>
              ) : null}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
