class SecurityService:

    def analyze(self, code: str):

        code = code.strip()

        if not code:
            raise ValueError("Code cannot be empty.")

        vulnerabilities = []

        security_patterns = [
            (
                "password",
                "Potential hardcoded password detected.",
                "high"
            ),
            (
                "api_key",
                "Potential hardcoded API key detected.",
                "high"
            ),
            (
                "secret",
                "Potential hardcoded secret detected.",
                "high"
            ),
            (
                "eval(",
                "Use of eval() can execute arbitrary code.",
                "critical"
            ),
            (
                "exec(",
                "Use of exec() can execute arbitrary code.",
                "critical"
            )
        ]

        code_lower = code.lower()

        for pattern, message, severity in security_patterns:

            if pattern.lower() in code_lower:

                vulnerabilities.append({
                    "pattern": pattern,
                    "message": message,
                    "severity": severity
                })

        if vulnerabilities:
            status = "security_issues_found"
            summary = "Potential security vulnerabilities detected."
        else:
            status = "security_check_passed"
            summary = "No obvious security vulnerabilities detected."

        return {
            "status": status,
            "summary": summary,
            "vulnerabilities": vulnerabilities,
            "total_vulnerabilities": len(vulnerabilities),
            "next_stage": "performance_analysis"
        }