import json
import os
import sys
from backend.db.connection import get_connection
from sqlalchemy import text


def handle_tool_call(tool_name: str, arguments: dict) -> str:
    if tool_name == "analyze_repo":
        repo_path = arguments.get("repo_path", "")
        try:
            from backend.services.repo_analyzer import analyze_repo
            report = analyze_repo(repo_path)
            return json.dumps({
                "overall_score": report["overall_score"],
                "grade": report["grade"],
                "issues": report["all_issues"][:5]
            })
        except ValueError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            return json.dumps({"error": f"analyze_repo failed: {str(e)}"})

    elif tool_name == "get_review_history":
        try:
            if not os.getenv("DATABASE_URL"):
                return json.dumps(
                    {
                        "error": (
                            "Review history is not configured in this deployment yet. "
                            "Set up a hosted Postgres/Cloud SQL database first."
                        )
                    }
                )
            limit = arguments.get("limit", 5)
            with get_connection() as conn:
                rows = conn.execute(
                    text("SELECT repo_path, overall_score, grade, created_at FROM repo_reviews ORDER BY created_at DESC LIMIT :limit"),
                    {"limit": limit}
                ).fetchall()
            history = [
                {"repo": r[0], "score": r[1], "grade": r[2], "at": str(r[3])}
                for r in rows
            ]
            return json.dumps(history)
        except Exception as e:
            return json.dumps({"error": f"get_review_history failed: {str(e)}"})

    elif tool_name == "ask_course_assistant":
        try:
            from backend.services.course_assistant import ask_course_assistant
            question = arguments.get("question", "")
            result = ask_course_assistant(question)
            return json.dumps({"answer": result["answer"]})
        except Exception as e:
            return json.dumps({"error": f"ask_course_assistant failed: {str(e)}"})

    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})


ALL_TOOLS = [
    {
        "name": "analyze_repo",
        "description": "Analyze a student's GitHub repo or local path for code quality, security, and documentation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Local path or GitHub URL of the repo to analyze"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "get_review_history",
        "description": "Fetch the most recent repo review results from the database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "How many recent reviews to return (default 5)"
                }
            },
            "required": []
        }
    },
    {
        "name": "ask_course_assistant",
        "description": "Ask a question about CMSC389A course content, assignments, or schedule.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to ask about the course"
                }
            },
            "required": ["question"]
        }
    }
]


def get_tools() -> list[dict]:
    if os.getenv("DATABASE_URL"):
        return ALL_TOOLS

    return [tool for tool in ALL_TOOLS if tool["name"] != "get_review_history"]


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = message.get("method")
        msg_id = message.get("id")

        # Notifications have no id — they are one-way, don't respond
        if msg_id is None:
            continue

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "repomentor", "version": "1.0.0"}
                }
            }

        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": get_tools()}
            }

        elif method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result_text = handle_tool_call(tool_name, arguments)
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": result_text}]
                }
            }

        else:
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": "Method not found"}
            }

        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
