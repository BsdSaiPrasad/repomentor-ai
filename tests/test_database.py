import pytest
from backend.db.connection import save_review, get_connection
from sqlalchemy import text


def test_save_review_returns_an_id():
    review_id = save_review(
        repo_path="tests/fake_repo",
        overall_score=75.0,
        grade="Good",
        breakdown=[]
    )
    assert isinstance(review_id, int)
    assert review_id > 0


def test_save_review_stores_correct_score():
    review_id = save_review(
        repo_path="tests/fake_repo",
        overall_score=88.5,
        grade="Good",
        breakdown=[]
    )
    with get_connection() as conn:
        row = conn.execute(
            text("SELECT overall_score FROM repo_reviews WHERE id = :id"),
            {"id": review_id}
        ).fetchone()
    assert row[0] == 88.5


def test_save_review_stores_agent_runs():
    breakdown = [
        {"agent": "Code Review Agent", "score": 80.0, "summary": "OK", "duration": 1.0, "issues": []},
        {"agent": "Security Agent", "score": 70.0, "summary": "Fine", "duration": 1.2, "issues": []},
    ]
    review_id = save_review("tests/fake_repo", 75.0, "Good", breakdown)
    with get_connection() as conn:
        rows = conn.execute(
            text("SELECT agent_name FROM agent_runs WHERE review_id = :id"),
            {"id": review_id}
        ).fetchall()
    agent_names = [r[0] for r in rows]
    assert "Code Review Agent" in agent_names
    assert "Security Agent" in agent_names


def test_save_review_stores_issues():
    breakdown = [
        {"agent": "Security Agent", "score": 60.0, "summary": "Bad", "duration": 1.0,
         "issues": ["Hardcoded password", "eval() used"]},
    ]
    review_id = save_review("tests/fake_repo", 60.0, "Needs Improvement", breakdown)
    with get_connection() as conn:
        agent_row = conn.execute(
            text("SELECT id FROM agent_runs WHERE review_id = :id"),
            {"id": review_id}
        ).fetchone()
        issues = conn.execute(
            text("SELECT issue_text FROM issues WHERE agent_run_id = :id"),
            {"id": agent_row[0]}
        ).fetchall()
    issue_texts = [i[0] for i in issues]
    assert "Hardcoded password" in issue_texts
    assert "eval() used" in issue_texts
