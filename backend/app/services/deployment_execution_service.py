import subprocess
from pathlib import Path


class DeploymentExecutionService:

    def deploy(
        self,
        repository_path: str,
        command: str
    ):

        repository = Path(
            repository_path
        ).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                "Repository path does not exist."
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                "Repository path is not a directory."
            )

        command = command.strip()

        if not command:
            raise ValueError(
                "Deployment command cannot be empty."
            )

        result = subprocess.run(
            command,
            cwd=repository,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            status = "deployment_completed"
            next_stage = "monitoring"

        else:

            status = "deployment_failed"
            next_stage = "failure_diagnosis"

        return {
            "repository": str(repository),
            "command": command,
            "return_code": result.returncode,
            "status": status,
            "output": result.stdout,
            "error": result.stderr,
            "next_stage": next_stage
        }