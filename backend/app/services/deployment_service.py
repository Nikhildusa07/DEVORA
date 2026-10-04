from pathlib import Path


class DeploymentService:

    def check_readiness(self, repository_path: str):

        repository = Path(repository_path).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                "Repository path does not exist."
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                "Repository path is not a directory."
            )

        required_files = [
            "main.py",
            "requirements.txt"
        ]

        missing_files = []

        for file_name in required_files:
            if not (repository / file_name).exists():
                missing_files.append(file_name)

        if missing_files:
            status = "deployment_not_ready"
            summary = "Required deployment files are missing."
        else:
            status = "deployment_ready"
            summary = "Repository is ready for deployment review."

        return {
            "repository": str(repository),
            "status": status,
            "summary": summary,
            "missing_files": missing_files,
            "next_stage": (
                "deployment"
                if not missing_files
                else "deployment_configuration"
            )
        }