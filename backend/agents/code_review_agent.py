import os
from dotenv import load_dotenv
from backend.agents.base_agent import BaseAgent, AgentResult
from backend.llm.groq_client import extract_groq_text, groq_chat_completion

load_dotenv()

class CodeReviewAgent(BaseAgent):
    name = "Code Review Agent"

    def run(self, repo_path: str) -> AgentResult:
        code = self._read_code(repo_path)

        prompt = f"""You are an expert code reviewer for a university programming course.

Review this Python code and evaluate:
1. Code structure and organization
2. Function naming and readability  
3. Type hints usage
4. Docstrings and comments
5. Error handling

Code to review:
{code}

Respond in this exact format:
SCORE: [0-100]
SUMMARY: [one sentence]
ISSUES:
- Severity: [High/Medium/Low/Potential] | Location: [file path or function name] | Issue: [specific issue] | Fix: [short actionable fix]
[include at most 3 issues, only the most important ones]
DETAILS: [two short sentences max]"""

        response = groq_chat_completion(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )

        text = extract_groq_text(response)
        score = self._extract_score(text)

        return AgentResult(
            agent_name=self.name,
            score=score,
            summary=self._extract_section(text, "SUMMARY"),
            details=self._extract_section(text, "DETAILS"),
            issues=self._extract_issues(text)
        )

    def _read_code(self, repo_path: str) -> str:
        code = ""
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r") as f:
                        relpath = os.path.relpath(filepath, repo_path)
                        code += f"\n# File: {relpath}\n{f.read()}"
        return code[:3000]
