from pathlib import Path


class RefactoringService:

    def analyze(
        self,
        repository_path: str,
        file_path: str
    ):

        repository = Path(repository_path).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                "Repository path does not exist."
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                "Repository path is not a directory."
            )

        file_path = file_path.strip()

        if not file_path:
            raise ValueError(
                "File path cannot be empty."
            )

        target_file = (
            repository / file_path
        ).resolve()

        try:
            target_file.relative_to(repository)
        except ValueError:
            raise ValueError(
                "File path must remain inside the repository."
            )

        if not target_file.exists():
            raise FileNotFoundError(
                "Target file does not exist."
            )

        if not target_file.is_file():
            raise ValueError(
                "Target path is not a file."
            )

        content = target_file.read_text(
            encoding="utf-8"
        )

        recommendations = []

        if "print(" in content:
            recommendations.append({
                "type": "debug_code",
                "message": "Remove debug print statements.",
                "severity": "low"
            })

        if "except:" in content:
            recommendations.append({
                "type": "exception_handling",
                "message": "Replace bare except with specific exceptions.",
                "severity": "medium"
            })

        if content.count("if ") > 5:
            recommendations.append({
                "type": "complexity",
                "message": "Consider simplifying complex conditional logic.",
                "severity": "medium"
            })

        if len(content.splitlines()) > 300:
            recommendations.append({
                "type": "maintainability",
                "message": "Consider splitting the large file into smaller modules.",
                "severity": "medium"
            })

        if recommendations:
            status = "refactoring_recommended"
            summary = "Potential refactoring opportunities detected."
        else:
            status = "refactoring_check_passed"
            summary = "No obvious refactoring issues detected."

        return {
            "repository": str(repository),
            "file": str(
                target_file.relative_to(repository)
            ),
            "status": status,
            "summary": summary,
            "recommendations": recommendations,
            "total_recommendations": len(
                recommendations
            ),
            "next_stage": "code_review"
        }