import os
from groq import Groq
from dotenv import load_dotenv
from backend.agents.base_agent import BaseAgent, AgentResult

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class DocumentationAgent(BaseAgent):
    """
    Checks if the repo has proper documentation — README, docstrings, comments.
    
    Example:
        agent = DocumentationAgent()
        result = agent.run("sample_repos/good_student")
        result.score    # 95.0
        result.summary  # "Excellent documentation with clear README"
    """
    name = "Documentation Agent"

    def run(self, repo_path: str) -> AgentResult:
        readme = self._read_readme(repo_path)
        code = self._read_code(repo_path)

        prompt = f"""You are a documentation reviewer for a university programming course.

Review this student repo for documentation quality:
1. Does it have a README? Is it detailed enough?
2. Do functions have docstrings explaining what they do?
3. Are there helpful inline comments?
4. Is the code self-explanatory with good variable names?

README content:
{readme}

Code:
{code}

Respond in this exact format:
SCORE: [0-100]
SUMMARY: [one sentence]
ISSUES:
- Severity: [High/Medium/Low/Potential] | Location: [file path or function name] | Issue: [specific issue] | Fix: [short actionable fix]
[include at most 3 issues, only the most important ones]
DETAILS: [two short sentences max]"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512
        )

        text = response.choices[0].message.content
        score = self._extract_score(text)

        return AgentResult(
            agent_name=self.name,
            score=score,
            summary=self._extract_section(text, "SUMMARY"),
            details=self._extract_section(text, "DETAILS"),
            issues=self._extract_issues(text)
        )

    def _read_readme(self, repo_path: str) -> str:
        for filename in ["README.md", "readme.md", "README.txt"]:
            filepath = os.path.join(repo_path, filename)
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    return f.read()
        return "No README found"

    def _read_code(self, repo_path: str) -> str:
        code = ""
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r") as f:
                        relpath = os.path.relpath(filepath, repo_path)
                        code += f"\n# File: {relpath}\n{f.read()}"
        return code[:2000]
