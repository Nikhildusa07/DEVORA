import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv()


class AIImplementationService:

    MODELS = [
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-3.8-flash"
    ]

    PROTECTED_FILES = {
        "main.py"
    }

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def _get_repository_files(
        self,
        repository_path: str
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

        ignored = {
            ".git",
            "venv",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            "node_modules"
        }

        files = []

        for path in repository.rglob("*"):

            if not path.is_file():
                continue

            if any(
                part in ignored
                for part in path.parts
            ):
                continue

            files.append(
                str(
                    path.relative_to(
                        repository
                    )
                )
            )

        return repository, files

    def _generate(
        self,
        model: str,
        prompt: str
    ):

        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError(
                "AI returned an empty response."
            )

        return response.text

    def generate_implementation(
        self,
        requirement: str,
        reasoning: str,
        repository_path: str
    ):

        requirement = requirement.strip()
        reasoning = reasoning.strip()

        if not requirement:
            raise ValueError(
                "Requirement cannot be empty."
            )

        if not reasoning:
            raise ValueError(
                "AI reasoning cannot be empty."
            )

        repository, files = (
            self._get_repository_files(
                repository_path
            )
        )

        repository_files = "\n".join(files)

        prompt = f"""
You are DEVORA, an autonomous AI
software engineering implementation engine.

Generate the actual code changes required
to implement the requirement inside the
existing repository.

REQUIREMENT:
{requirement}

AI REASONING:
{reasoning}

EXISTING REPOSITORY FILES:
{repository_files}

RULES:

1. Generate only necessary files.
2. Prefer modifying existing files when appropriate.
3. Never delete existing files.
4. Never modify .env files.
5. Never modify .git configuration.
6. Never modify virtual environments.
7. Never generate secrets or API keys.
8. Preserve the existing architecture.
9. Use the technologies already present in the repository.
10. Do not introduce a new database framework unless required.
11. Include appropriate pytest tests.
12. Every generated file must contain complete content.
13. NEVER modify the repository root main.py.
14. The repository root main.py is protected infrastructure.
15. Return ONLY valid JSON.
16. Do not use markdown code fences.

JSON FORMAT:

{{
    "summary": "short implementation summary",
    "files": [
        {{
            "path": "relative/path/to/file.py",
            "action": "create",
            "content": "complete file content"
        }}
    ]
}}
"""

        errors = []

        for model in self.MODELS:

            try:

                result = self._generate(
                    model,
                    prompt
                )

                result = result.strip()

                if result.startswith("```json"):
                    result = result[7:]

                if result.startswith("```"):
                    result = result[3:]

                if result.endswith("```"):
                    result = result[:-3]

                result = result.strip()

                implementation = json.loads(
                    result
                )

                if not isinstance(
                    implementation,
                    dict
                ):
                    raise ValueError(
                        "AI implementation response "
                        "must be a JSON object."
                    )

                files_result = implementation.get(
                    "files"
                )

                if not isinstance(
                    files_result,
                    list
                ):
                    raise ValueError(
                        "AI implementation response "
                        "must contain a files list."
                    )

                return {
                    "status": "implementation_generated",
                    "model": model,
                    "repository": str(
                        repository
                    ),
                    "summary": implementation.get(
                        "summary",
                        ""
                    ),
                    "files": files_result,
                    "total_files": len(
                        files_result
                    ),
                    "next_stage": "apply_changes"
                }

            except Exception as error:

                errors.append({
                    "model": model,
                    "error": str(error)
                })

        raise RuntimeError(
            "AI implementation generation failed. "
            f"Attempts: {errors}"
        )

    def apply_changes(
        self,
        repository_path: str,
        implementation: dict
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

        files = implementation.get(
            "files",
            []
        )

        if not files:
            return {
                "status": "implementation_applied",
                "repository": str(repository),
                "changed_files": [],
                "skipped_files": [],
                "total_files": 0,
                "next_stage": "testing"
            }

        changed_files = []
        skipped_files = []

        protected_directories = {
            ".git",
            "venv",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            "node_modules"
        }

        for file_data in files:

            if not isinstance(
                file_data,
                dict
            ):
                raise ValueError(
                    "Invalid implementation file definition."
                )

            file_path = str(
                file_data.get(
                    "path",
                    ""
                )
            ).strip()

            action = str(
                file_data.get(
                    "action",
                    "create"
                )
            ).strip().lower()

            content = file_data.get(
                "content",
                ""
            )

            if not file_path:
                raise ValueError(
                    "Implementation contains "
                    "an empty file path."
                )

            normalized_path = file_path.replace(
                "\\",
                "/"
            ).strip("/")

            if normalized_path in self.PROTECTED_FILES:

                skipped_files.append(
                    normalized_path
                )

                continue

            if action not in {
                "create",
                "modify"
            }:
                raise ValueError(
                    f"Unsupported file action: {action}"
                )

            target_file = (
                repository / file_path
            ).resolve()

            try:

                target_file.relative_to(
                    repository
                )

            except ValueError:

                raise ValueError(
                    "Implementation file path "
                    "must remain inside the repository."
                )

            if any(
                part in protected_directories
                for part in target_file.parts
            ):

                raise ValueError(
                    "Implementation cannot modify "
                    "protected directories."
                )

            if target_file.name == ".env":

                raise ValueError(
                    "Implementation cannot modify .env."
                )

            if not isinstance(
                content,
                str
            ):
                raise ValueError(
                    "File content must be a string."
                )

            target_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            target_file.write_text(
                content,
                encoding="utf-8"
            )

            changed_files.append(
                str(
                    target_file.relative_to(
                        repository
                    )
                )
            )

        return {
            "status": "implementation_applied",
            "repository": str(repository),
            "changed_files": changed_files,
            "skipped_files": skipped_files,
            "total_files": len(
                changed_files
            ),
            "next_stage": "testing"
        }