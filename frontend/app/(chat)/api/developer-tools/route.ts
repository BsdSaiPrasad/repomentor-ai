import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.REPOMENTOR_API_BASE_URL ?? "http://127.0.0.1:8001";

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/mcp-tools`, {
      cache: "no-store",
    });

    const raw = await response.text();
    let payload: unknown = {};

    try {
      payload = raw ? JSON.parse(raw) : {};
    } catch {
      payload = { error: raw || "Could not parse MCP tool list." };
    }

    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: "Could not reach the MCP tools backend." },
      { status: 500 },
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const response = await fetch(`${API_BASE_URL}/api/v1/mcp-tools/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const raw = await response.text();
    let payload: unknown = {};

    try {
      payload = raw ? JSON.parse(raw) : {};
    } catch {
      payload = { error: raw || "Could not parse MCP tool response." };
    }

    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: "Could not run the selected MCP tool." },
      { status: 500 },
    );
  }
}
