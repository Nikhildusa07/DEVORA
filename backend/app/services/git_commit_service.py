import subprocess
from pathlib import Path


class GitCommitService:

    def commit_changes(
        self,
        repository_path: str,
        message: str
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

        message = message.strip()

        if not message:
            raise ValueError(
                "Commit message cannot be empty."
            )

        add_result = subprocess.run(
            [
                "git",
                "add",
                "."
            ],
            cwd=repository,
            capture_output=True,
            text=True
        )

        if add_result.returncode != 0:
            raise RuntimeError(
                add_result.stderr.strip()
                or "Git add failed."
            )

        commit_result = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                message
            ],
            cwd=repository,
            capture_output=True,
            text=True
        )

        if commit_result.returncode != 0:
            raise RuntimeError(
                commit_result.stderr.strip()
                or "Git commit failed."
            )

        return {
            "repository": str(repository),
            "status": "committed",
            "message": message,
            "output": commit_result.stdout.strip(),
            "next_stage": "pull_request"
        }