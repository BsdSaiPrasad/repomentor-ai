from dataclasses import dataclass

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
