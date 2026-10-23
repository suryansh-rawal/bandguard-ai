from typing import List, Dict, Any, Tuple

class ConfidenceRouter:
    """
    K9: Confidence Routing Service.
    Computes document compliance confidence score (0-100) and routes content
    into Green, Yellow, or Red review workflows based on issue severity and density.
    """

    CRITICAL_PENALTY = 25.0
    WARNING_PENALTY = 12.0
    SUGGESTION_PENALTY = 3.0

    def compute_routing(self, issues: List[Dict[str, Any]]) -> Tuple[float, str, Dict[str, int]]:
        """
        Evaluate issues and return (confidence_score, confidence_rating, summary_dict).
        Ratings:
          - 'green': High confidence (score >= 85, 0 critical issues)
          - 'yellow': Moderate confidence (60 <= score < 85 or minor warnings)
          - 'red': Low confidence / blocked (score < 60 or >= 1 critical issue)
        """
        critical_count = sum(1 for i in issues if i.get("severity") == "critical")
        warning_count = sum(1 for i in issues if i.get("severity") == "warning")
        suggestion_count = sum(1 for i in issues if i.get("severity") == "suggestion")
        total_issues = len(issues)

        # Calculate penalty deduction
        total_deduction = (
            (critical_count * self.CRITICAL_PENALTY) +
            (warning_count * self.WARNING_PENALTY) +
            (suggestion_count * self.SUGGESTION_PENALTY)
        )

        raw_score = max(0.0, min(100.0, 100.0 - total_deduction))
        score = round(raw_score, 1)

        # Routing decision
        if critical_count > 0 or score < 60.0:
            rating = "red"
        elif warning_count > 0 or score < 85.0:
            rating = "yellow"
        else:
            rating = "green"

        summary = {
            "total_issues": total_issues,
            "critical": critical_count,
            "warning": warning_count,
            "suggestion": suggestion_count
        }

        return score, rating, summary

confidence_router = ConfidenceRouter()
