import subprocess
from pathlib import Path


class GitService:

    def get_status(self, repository_path: str):

        repository = Path(repository_path).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                "Repository path does not exist."
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                "Repository path is not a directory."
            )

        result = subprocess.run(
            [
                "git",
                "status",
                "--short",
                "--branch"
            ],
            cwd=repository,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
                or "Git status command failed."
            )

        return {
            "repository": str(repository),
            "status": "git_available",
            "output": result.stdout.strip(),
            "next_stage": "git_operations"
        }