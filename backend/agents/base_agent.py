from dataclasses import dataclass
import re

@dataclass
class AgentResult:
    agent_name: str
    score: float        # 0 to 100
    summary: str
    details: str
    issues: list
    duration: float = 0.0

class BaseAgent:
    """
    Every agent inherits from this class and must implement the run() method.
    
    This is the Strategy design pattern — each agent has a different strategy
    for reviewing code, but they all share the same interface (run method).
    
    Example:
        agent = CodeReviewAgent()
        result = agent.run("/path/to/repo")
        result.score   # 85.0
        result.summary # "Good code quality with minor issues"
    """
    name = "BaseAgent"

    def run(self, repo_path: str) -> AgentResult:
        raise NotImplementedError("Each agent must implement run()")

    def _extract_score(self, text: str) -> float:
        for line in text.split("\n"):
            if line.startswith("SCORE:"):
                try:
                    return float(line.replace("SCORE:", "").strip())
                except Exception:
                    return 50.0
        return 50.0

    def _extract_section(self, text: str, section: str) -> str:
        for line in text.split("\n"):
            if line.startswith(f"{section}:"):
                return line.replace(f"{section}:", "").strip()
        return ""

    def _extract_issues(self, text: str) -> list[dict]:
        issues = []
        in_issues = False
        for line in text.split("\n"):
            if line.startswith("ISSUES:"):
                in_issues = True
                continue
            if in_issues and line.startswith("DETAILS:"):
                break
            if not in_issues or not line.strip():
                continue

            cleaned = line.strip()
            if cleaned[0] not in ("-", "*", "•") and not (cleaned[0].isdigit() and "." in cleaned[:3]):
                continue

            issue_text = re.sub(r"^[-*•]\s*", "", cleaned)
            issue_text = re.sub(r"^\d+\.\s*", "", issue_text)
            issues.append(self._parse_issue_line(issue_text))
        return issues

    def _parse_issue_line(self, issue_text: str) -> dict:
        result = {
            "severity": "Medium",
            "location": "Not specified",
            "issue": issue_text.strip(),
            "fix": "Add a more specific fix recommendation.",
        }

        parts = [part.strip() for part in issue_text.split("|")]
        for part in parts:
            if ":" not in part:
                continue
            key, value = part.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key == "severity":
                result["severity"] = value
            elif key == "location":
                result["location"] = value
            elif key == "issue":
                result["issue"] = value
            elif key == "fix":
                result["fix"] = value
        return result
