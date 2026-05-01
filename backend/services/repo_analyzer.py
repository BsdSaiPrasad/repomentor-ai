import asyncio
import subprocess
import tempfile
import shutil
import os
import time
from backend.agents.code_review_agent import CodeReviewAgent
from backend.agents.security_agent import SecurityAgent
from backend.agents.documentation_agent import DocumentationAgent
from backend.agents.synthesizer_agent import SynthesizerAgent

async def run_agent_async(agent, repo_path: str, status_callback=None):
    """
    Run a single agent in a thread and track how long it takes.
    status_callback is an optional function called when agent finishes.
    """
    loop = asyncio.get_event_loop()
    start = time.time()
    result = await loop.run_in_executor(None, agent.run, repo_path)
    duration = round(time.time() - start, 1)
    result.duration = duration
    if status_callback:
        status_callback(agent.name, result.score, duration)
    return result

async def analyze_repo_async(repo_path: str, status_callback=None) -> dict:
    """
    Run all 3 agents concurrently using asyncio.gather().
    """
    agents = [
        CodeReviewAgent(),
        SecurityAgent(),
        DocumentationAgent()
    ]

    results = await asyncio.gather(*[
        run_agent_async(agent, repo_path, status_callback) for agent in agents
    ])

    synthesizer = SynthesizerAgent()
    final_report = synthesizer.synthesize(list(results))

    # Add timing to breakdown
    for i, result in enumerate(results):
        final_report["breakdown"][i]["duration"] = result.duration

    return final_report

def clone_repo(github_url: str) -> str:
    tmp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", github_url, tmp_dir],
                   capture_output=True, timeout=60)
    return tmp_dir

def analyze_repo(repo_path: str, status_callback=None) -> dict:
    """
    Entry point called from Streamlit.
    Accepts either a local path or a GitHub URL.
    status_callback(agent_name, score, duration) is called when each agent finishes.
    """
    tmp_dir = None

    if repo_path.startswith("https://github.com"):
        tmp_dir = clone_repo(repo_path)
        actual_path = tmp_dir
        py_files = [f for r, d, files in os.walk(actual_path) for f in files if f.endswith(".py")]
        if not py_files:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise ValueError("Could not clone repo or no Python files found. Check the URL.")
    else:
        actual_path = repo_path
        if not os.path.exists(actual_path):
            raise ValueError(f"Path '{actual_path}' does not exist.")
        py_files = [f for r, d, files in os.walk(actual_path) for f in files if f.endswith(".py")]
        if not py_files:
            raise ValueError(f"No Python files found in '{actual_path}'.")

    try:
        result = asyncio.run(analyze_repo_async(actual_path, status_callback))
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return result
