import os
import subprocess
import sys
from pathlib import Path


class TestExecutionService:

    TEST_TIMEOUT_SECONDS = 120

    def execute_tests(self, repository_path: str):

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

        tests_directory = repository / "tests"

        if not tests_directory.exists():
            backend_tests_directory = (
                repository / "backend" / "tests"
            )

            if backend_tests_directory.exists():
                test_target = "backend/tests"

            else:
                test_target = "tests"

        else:
            test_target = "tests"

        command = [
            sys.executable,
            "-m",
            "pytest",
            test_target,
            "-q"
        ]

        environment = os.environ.copy()

        environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

        python_paths = [
            str(repository)
        ]

        backend_directory = repository / "backend"

        if backend_directory.exists():
            python_paths.append(
                str(backend_directory)
            )

        existing_pythonpath = environment.get(
            "PYTHONPATH",
            ""
        )

        if existing_pythonpath:
            python_paths.append(
                existing_pythonpath
            )

        environment["PYTHONPATH"] = (
            os.pathsep.join(python_paths)
        )

        creation_flags = 0

        if os.name == "nt":
            creation_flags = (
                subprocess.CREATE_NEW_PROCESS_GROUP
            )

        try:

            result = subprocess.run(
                command,
                cwd=repository,
                capture_output=True,
                text=True,
                timeout=self.TEST_TIMEOUT_SECONDS,
                env=environment,
                creationflags=creation_flags
            )

            return {
                "repository": str(repository),
                "command": (
                    f"pytest {test_target} -q"
                ),
                "return_code": result.returncode,
                "status": (
                    "passed"
                    if result.returncode == 0
                    else "failed"
                ),
                "output": result.stdout,
                "error": result.stderr,
                "timeout": False,
                "next_stage": (
                    "review"
                    if result.returncode == 0
                    else "failure_diagnosis"
                )
            }

        except subprocess.TimeoutExpired as error:

            output = ""

            if error.stdout:
                output = (
                    error.stdout.decode()
                    if isinstance(
                        error.stdout,
                        bytes
                    )
                    else error.stdout
                )

            error_output = ""

            if error.stderr:
                error_output = (
                    error.stderr.decode()
                    if isinstance(
                        error.stderr,
                        bytes
                    )
                    else error.stderr
                )

            return {
                "repository": str(repository),
                "command": (
                    f"pytest {test_target} -q"
                ),
                "return_code": -1,
                "status": "failed",
                "output": output,
                "error": (
                    "Test execution timed out after "
                    f"{self.TEST_TIMEOUT_SECONDS} seconds.\n"
                    f"{error_output}"
                ),
                "timeout": True,
                "next_stage": "failure_diagnosis"
            }