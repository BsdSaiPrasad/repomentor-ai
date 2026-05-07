import { NextResponse } from "next/server";

const backendBaseUrl =
  process.env.REPOMENTOR_API_BASE_URL ?? "http://127.0.0.1:8001";

type CourseAssistantRequest = {
  messages?: Array<{
    role: string;
    content: string;
  }>;
  question?: string;
};

export async function POST(request: Request) {
  let payload: CourseAssistantRequest;

  try {
    payload = (await request.json()) as CourseAssistantRequest;
  } catch {
    return NextResponse.json(
      { error: "Invalid request body." },
      { status: 400 },
    );
  }

  const messages = Array.isArray(payload.messages) ? payload.messages : [];
  const latestQuestion =
    typeof payload.question === "string" && payload.question.trim()
      ? payload.question.trim()
      : messages
          .filter((message) => message.role === "user")
          .at(-1)
          ?.content?.trim();

  if (!latestQuestion) {
    return NextResponse.json(
      { error: "A question is required." },
      { status: 400 },
    );
  }

  try {
    const backendResponse = await fetch(
      `${backendBaseUrl}/api/v1/course-assistant/chat`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages:
            messages.length > 0
              ? messages
              : [{ role: "user", content: latestQuestion }],
        }),
      },
    );

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: data?.detail ?? data?.error ?? "Course assistant failed." },
        { status: backendResponse.status },
      );
    }

    return NextResponse.json({
      answer: data.answer ?? "I couldn't generate an answer.",
      sources: Array.isArray(data.sources) ? data.sources : [],
    });
  } catch {
    return NextResponse.json(
      { error: "Could not reach the course assistant service." },
      { status: 502 },
    );
  }
}
