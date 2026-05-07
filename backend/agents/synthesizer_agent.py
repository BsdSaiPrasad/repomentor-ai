from backend.agents.base_agent import AgentResult

class SynthesizerAgent:
    """
    Combines results from all agents into one final report.
    
    Think of it as the head professor who reads all 3 expert reports
    and writes the final grade and feedback for the student.
    
    Example:
        results = [code_result, security_result, doc_result]
        synthesizer = SynthesizerAgent()
        final = synthesizer.synthesize(results)
        final["overall_score"]  # 78.3
        final["summary"]        # combined summary
    """
    name = "Synthesizer"

    def synthesize(self, results: list[AgentResult]) -> dict:
        # Calculate overall score as average of all agent scores
        scores = [r.score for r in results]
        overall_score = round(sum(scores) / len(scores), 1)

        # Collect all issues from all agents
        all_issues = []
        for result in results:
            for issue in result.issues:
                all_issues.append({
                    "agent": result.agent_name,
                    "severity": issue.get("severity", "Medium"),
                    "location": issue.get("location", "Not specified"),
                    "issue": issue.get("issue", ""),
                    "fix": issue.get("fix", ""),
                })

        # Build per-agent breakdown
        breakdown = []
        for result in results:
            breakdown.append({
                "agent": result.agent_name,
                "score": result.score,
                "summary": result.summary,
                "issues": result.issues
            })

        # Determine grade label
        if overall_score >= 90:
            grade = "Excellent"
        elif overall_score >= 75:
            grade = "Good"
        elif overall_score >= 60:
            grade = "Needs Improvement"
        else:
            grade = "Poor"

        return {
            "overall_score": overall_score,
            "grade": grade,
            "breakdown": breakdown,
            "all_issues": all_issues,
            "agent_count": len(results)
        }
