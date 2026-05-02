-- RepoMentor AI — PostgreSQL Schema

CREATE TABLE IF NOT EXISTS repo_reviews (
    id SERIAL PRIMARY KEY,
    repo_path TEXT NOT NULL,
    overall_score FLOAT NOT NULL,
    grade TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    review_id INTEGER REFERENCES repo_reviews(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    score FLOAT NOT NULL,
    summary TEXT,
    duration FLOAT
);

CREATE TABLE IF NOT EXISTS issues (
    id SERIAL PRIMARY KEY,
    agent_run_id INTEGER REFERENCES agent_runs(id) ON DELETE CASCADE,
    issue_text TEXT NOT NULL
);
