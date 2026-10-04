from pathlib import Path


class CICDService:

    def analyze(self, repository_path: str):

        repository = Path(repository_path).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                "Repository path does not exist."
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                "Repository path is not a directory."
            )

        workflow_directory = (
            repository / ".github" / "workflows"
        )

        workflows = []

        if workflow_directory.exists():

            for workflow in workflow_directory.iterdir():

                if workflow.is_file() and workflow.suffix in {
                    ".yml",
                    ".yaml"
                }:
                    workflows.append(
                        workflow.name
                    )

        if workflows:

            status = "ci_cd_configured"
            summary = "CI/CD workflow configuration detected."

        else:

            status = "ci_cd_not_configured"
            summary = "No CI/CD workflow configuration detected."

        return {
            "repository": str(repository),
            "workflows": workflows,
            "total_workflows": len(workflows),
            "status": status,
            "summary": summary,
            "next_stage": (
                "deployment"
                if workflows
                else "ci_cd_configuration"
            )
        }