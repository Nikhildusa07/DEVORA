class PerformanceService:

    def analyze(self, code: str):

        code = code.strip()

        if not code:
            raise ValueError("Code cannot be empty.")

        issues = []

        if "for " in code and "range(len(" in code:
            issues.append({
                "type": "performance",
                "message": "Potential inefficient loop detected.",
                "severity": "medium"
            })

        if ".append(" in code:
            issues.append({
                "type": "performance",
                "message": "Repeated list append operations detected; review for possible optimization.",
                "severity": "low"
            })

        if "while True:" in code:
            issues.append({
                "type": "performance",
                "message": "Infinite loop pattern detected; verify termination logic.",
                "severity": "high"
            })

        if issues:
            status = "performance_issues_found"
            summary = "Potential performance issues detected."
        else:
            status = "performance_check_passed"
            summary = "No obvious performance issues detected."

        return {
            "status": status,
            "summary": summary,
            "issues": issues,
            "total_issues": len(issues),
            "next_stage": "deployment_review"
        }