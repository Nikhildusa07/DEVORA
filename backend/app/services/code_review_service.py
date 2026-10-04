class CodeReviewService:

    def review(self, code: str):

        code = code.strip()

        if not code:
            raise ValueError("Code cannot be empty.")

        issues = []

        if "print(" in code:
            issues.append({
                "type": "quality",
                "message": "Debug print statement detected.",
                "severity": "low"
            })

        if "except:" in code:
            issues.append({
                "type": "quality",
                "message": "Bare except statement detected.",
                "severity": "medium"
            })

        if "password" in code.lower():
            issues.append({
                "type": "security",
                "message": "Potential hardcoded password detected.",
                "severity": "high"
            })

        if "api_key" in code.lower():
            issues.append({
                "type": "security",
                "message": "Potential hardcoded API key detected.",
                "severity": "high"
            })

        if not issues:
            status = "approved"
            summary = "No obvious code quality or security issues detected."
        else:
            status = "review_required"
            summary = "Potential code quality or security issues detected."

        return {
            "status": status,
            "summary": summary,
            "issues": issues,
            "total_issues": len(issues),
            "next_stage": "security_analysis"
        }