import os
import subprocess
from groq import Groq
from dotenv import load_dotenv
from backend.agents.base_agent import BaseAgent, AgentResult

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class SecurityAgent(BaseAgent):
    """
    Scans for security vulnerabilities using Bandit + AI analysis.
    Uses Chain-of-Thought prompting — numbered reasoning steps.
    
    Example:
        agent = SecurityAgent()
        result = agent.run("sample_repos/bad_student")
        result.score    # 20.0 (low score = many issues)
        result.issues   # ["hardcoded password", "eval() usage", ...]
    """
    name = "Security Agent"

    def run(self, repo_path: str) -> AgentResult:
        bandit_output = self._run_bandit(repo_path)
        code = self._read_code(repo_path)

        # Chain-of-Thought prompt — numbered reasoning steps
        prompt = f"""You are a security expert reviewing student code for CMSC389A.

Think through this step by step:
1. First, identify any hardcoded secrets (passwords, API keys, tokens)
2. Then, check for dangerous functions (eval, exec, subprocess with shell=True)
3. Then, look for missing input validation
4. Then, check for insecure file operations
5. Finally, give an overall security score

Bandit scan results:
{bandit_output}

Code:
{code}

Respond in this exact format:
SCORE: [0-100]
SUMMARY: [one sentence]
ISSUES: [bullet points of each security issue]
DETAILS: [your step by step reasoning]"""

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

    def _run_bandit(self, repo_path: str) -> str:
        try:
            result = subprocess.run(
                ["bandit", "-r", repo_path, "-f", "txt"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout[:2000] if result.stdout else "No issues found by Bandit"
        except Exception as e:
            return f"Bandit scan failed: {str(e)}"

    def _read_code(self, repo_path: str) -> str:
        code = ""
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r") as f:
                        code += f"\n# File: {file}\n{f.read()}"
        return code[:2000]

    def _extract_score(self, text: str) -> float:
        for line in text.split("\n"):
            if line.startswith("SCORE:"):
                try:
                    return float(line.replace("SCORE:", "").strip())
                except:
                    return 50.0
        return 50.0

    def _extract_section(self, text: str, section: str) -> str:
        for line in text.split("\n"):
            if line.startswith(f"{section}:"):
                return line.replace(f"{section}:", "").strip()
        return ""

    def _extract_issues(self, text: str) -> list:
        issues = []
        in_issues = False
        for line in text.split("\n"):
            if line.startswith("ISSUES:"):
                in_issues = True
                first = line.replace("ISSUES:", "").strip()
                if first:
                    issues.append(first)
                continue
            if in_issues and line.startswith("DETAILS:"):
                break
            if in_issues and line.strip():
                cleaned = line.strip()
                if cleaned[0] in ("-", "*", "•") or (cleaned[0].isdigit() and "." in cleaned[:3]):
                    issues.append(cleaned)
        return issues
