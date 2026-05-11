import { NextResponse } from "next/server";

const backendBaseUrl =
  process.env.REPOMENTOR_API_BASE_URL ?? "http://127.0.0.1:8001";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await fetch(`${backendBaseUrl}/api/v1/app-factory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const raw = await response.text();
    let payload: Record<string, unknown> = {};

    try {
      payload = raw ? JSON.parse(raw) : {};
    } catch {
      payload = { error: raw || "App Factory request failed." };
    }

    if (!response.ok) {
      return NextResponse.json(
        { error: payload.error ?? payload.detail ?? "App Factory request failed." },
        { status: response.status },
      );
    }

    return NextResponse.json(payload);
  } catch {
    return NextResponse.json(
      { error: "Could not reach the App Factory backend." },
      { status: 502 },
    );
  }
}
