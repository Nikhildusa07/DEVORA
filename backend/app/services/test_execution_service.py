import subprocess
import sys
from pathlib import Path


class TestExecutionService:

    def execute_tests(self, repository_path: str):

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
                sys.executable,
                "-m",
                "pytest"
            ],
            cwd=repository,
            capture_output=True,
            text=True
        )

        return {
            "repository": str(repository),
            "command": "pytest",
            "return_code": result.returncode,
            "status": "passed" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "next_stage": (
                "review"
                if result.returncode == 0
                else "failure_diagnosis"
            )
        }