import subprocess
from pathlib import Path


class RollbackService:

    def rollback(
        self,
        repository_path: str,
        commit: str = "HEAD~1"
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

        status_result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain"
            ],
            cwd=repository,
            capture_output=True,
            text=True
        )

        if status_result.returncode != 0:
            raise RuntimeError(
                status_result.stderr.strip()
                or "Unable to check Git status."
            )

        if status_result.stdout.strip():
            raise RuntimeError(
                "Rollback stopped because the repository "
                "contains uncommitted changes."
            )

        commit = commit.strip()

        if not commit:
            raise ValueError(
                "Rollback commit cannot be empty."
            )

        result = subprocess.run(
            [
                "git",
                "reset",
                "--hard",
                commit
            ],
            cwd=repository,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
                or "Git rollback failed."
            )

        return {
            "repository": str(repository),
            "rollback_target": commit,
            "status": "rollback_completed",
            "output": result.stdout.strip(),
            "message": (
                "Repository successfully rolled back."
            ),
            "next_stage": "regression_detection"
        }