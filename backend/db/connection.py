import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/repomentor")

engine = create_engine(DATABASE_URL)

def get_connection():
    return engine.connect()

def save_review(repo_path: str, overall_score: float, grade: str, breakdown: list) -> int:
    """
    Saves a full repo review to the database.
    Returns the review_id of the inserted row.
    """
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO repo_reviews (repo_path, overall_score, grade)
                VALUES (:repo_path, :overall_score, :grade)
                RETURNING id
            """),
            {"repo_path": repo_path, "overall_score": overall_score, "grade": grade}
        )
        review_id = result.fetchone()[0]

        for agent in breakdown:
            agent_result = conn.execute(
                text("""
                    INSERT INTO agent_runs (review_id, agent_name, score, summary, duration)
                    VALUES (:review_id, :agent_name, :score, :summary, :duration)
                    RETURNING id
                """),
                {
                    "review_id": review_id,
                    "agent_name": agent["agent"],
                    "score": agent["score"],
                    "summary": agent.get("summary", ""),
                    "duration": agent.get("duration", 0)
                }
            )
            agent_run_id = agent_result.fetchone()[0]

            for issue in agent.get("issues", []):
                conn.execute(
                    text("INSERT INTO issues (agent_run_id, issue_text) VALUES (:agent_run_id, :issue_text)"),
                    {"agent_run_id": agent_run_id, "issue_text": issue}
                )

    return review_id
