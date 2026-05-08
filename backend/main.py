from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="RepoMentor AI",
    description="GenAI TA Toolkit for CMSC389A",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "RepoMentor AI"}

@app.get("/api/v1/status")
def status():
    return {"status": "running", "version": "0.1.0"}

@app.post("/api/v1/review")
def review_repo():
    return {"status": "not_implemented"}


class CourseQuestionRequest(BaseModel):
    question: str


class ChatMessage(BaseModel):
    role: str
    content: str


class CourseChatRequest(BaseModel):
    messages: list[ChatMessage]


class AssignmentRequest(BaseModel):
    topic: str
    difficulty: str
    refinement_notes: str | None = None


class RepoReviewRequest(BaseModel):
    repo_path: str


class MCPToolCallRequest(BaseModel):
    name: str
    arguments: dict = {}


@app.post("/api/v1/course-assistant")
def course_assistant(payload: CourseQuestionRequest):
    try:
        from backend.services.course_assistant import ask_course_assistant
        return ask_course_assistant(payload.question)
    except Exception as exc:
        return JSONResponse(
            {"error": f"Course assistant failed: {exc}"},
            status_code=500,
        )


@app.post("/api/v1/course-assistant/chat")
def course_assistant_chat(payload: CourseChatRequest):
    try:
        from backend.services.course_assistant import chat_course_assistant
        return chat_course_assistant([message.model_dump() for message in payload.messages])
    except Exception as exc:
        return JSONResponse(
            {"error": f"Course assistant chat failed: {exc}"},
            status_code=500,
        )


@app.post("/api/v1/assignment-builder")
def assignment_builder(payload: AssignmentRequest):
    try:
        from backend.services.assignment_generator import generate_assignment
        return generate_assignment(
            payload.topic,
            payload.difficulty,
            payload.refinement_notes or "",
        )
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse(
            {"error": f"Assignment builder failed: {exc}"},
            status_code=500,
        )


@app.post("/api/v1/repo-review")
def repo_review(payload: RepoReviewRequest):
    try:
        from backend.services.repo_analyzer import analyze_repo
        return analyze_repo(payload.repo_path)
    except Exception as exc:
        return JSONResponse(
            {"error": f"Repo review failed: {exc}"},
            status_code=500,
        )


@app.get("/api/v1/mcp-tools")
def list_mcp_tools():
    try:
        from backend.mcp_server.server import get_tools
        return {"tools": get_tools()}
    except Exception as exc:
        return JSONResponse(
            {"error": f"Could not load MCP tools: {exc}"},
            status_code=500,
        )


@app.post("/api/v1/mcp-tools/call")
def call_mcp_tool(payload: MCPToolCallRequest):
    try:
        from backend.mcp_server.server import handle_tool_call

        raw = handle_tool_call(payload.name, payload.arguments or {})
        try:
            import json

            return {"result": json.loads(raw)}
        except Exception:
            return {"result": raw}
    except Exception as exc:
        return JSONResponse(
            {"error": f"MCP tool call failed: {exc}"},
            status_code=500,
        )
