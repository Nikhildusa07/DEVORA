import subprocess
from pathlib import Path


class GitBranchService:

    def create_branch(
        self,
        repository_path: str,
        branch_name: str
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

        branch_name = branch_name.strip()

        if not branch_name:
            raise ValueError(
                "Branch name cannot be empty."
            )

        result = subprocess.run(
            [
                "git",
                "checkout",
                "-b",
                branch_name
            ],
            cwd=repository,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
                or "Git branch creation failed."
            )

        return {
            "repository": str(repository),
            "branch": branch_name,
            "status": "branch_created",
            "output": result.stdout.strip(),
            "next_stage": "pull_request"
        }