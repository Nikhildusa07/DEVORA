import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv()


class AIImplementationService:

    MODELS = [
        "gemini-3.5-flash",
        "gemini-3.6-flash"
    ]

    PROTECTED_FILES = {
        "main.py",
        "backend/main.py"
    }

    PROTECTED_DIRECTORIES = {
        ".git",
        "venv",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules"
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

        files = []

        for path in repository.rglob("*"):

            if not path.is_file():
                continue

            if any(
                part in self.PROTECTED_DIRECTORIES
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

    def _clean_json_response(
        self,
        result: str
    ):

        result = result.strip()

        if result.startswith("```json"):
            result = result[7:]

        elif result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        return result.strip()

    def _validate_implementation(
        self,
        files_result: list
    ):

        if not files_result:
            raise ValueError(
                "AI generated no implementation files."
            )

        production_files = []

        for file_data in files_result:

            if not isinstance(
                file_data,
                dict
            ):
                raise ValueError(
                    "Invalid implementation file definition."
                )

            path = str(
                file_data.get(
                    "path",
                    ""
                )
            ).strip()

            if not path:
                raise ValueError(
                    "Implementation contains an empty file path."
                )

            normalized_path = path.replace(
                "\\",
                "/"
            ).strip("/")

            filename = Path(
                normalized_path
            ).name.lower()

            if (
                filename.startswith("test_")
                or filename.endswith("_test.py")
                or "/tests/" in f"/{normalized_path}/"
            ):
                continue

            production_files.append(
                normalized_path
            )

        if not production_files:
            raise ValueError(
                "AI generated tests without production "
                "implementation. A real implementation "
                "must be generated before tests."
            )

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

Your job is to implement the user's requirement
inside the EXISTING repository.

REQUIREMENT:
{requirement}

AI REASONING:
{reasoning}

EXISTING REPOSITORY FILES:
{repository_files}

IMPORTANT IMPLEMENTATION RULES:

1. You MUST generate the actual production implementation.
2. Tests are supplementary and MUST NOT replace implementation.
3. NEVER return only test files.
4. Every requested feature must have corresponding
   production code.
5. If the requirement asks for an API endpoint:
   - create the required API route/module;
   - implement the endpoint;
   - use the existing FastAPI architecture;
   - integrate the route into the existing application
     using the project's existing routing mechanism.
6. If an existing router/module is appropriate,
   modify that existing production file.
7. If a new module is required, create the module.
8. The implementation must actually make the requested
   endpoint or feature reachable from the application.
9. After production implementation is generated,
   generate appropriate pytest tests for it.
10. Never generate tests for functionality that you
    did not implement.
11. Never delete existing files.
12. Never modify .env files.
13. Never modify .git configuration.
14. Never modify virtual environments.
15. Never generate secrets or API keys.
16. Preserve the existing architecture.
17. Use technologies already present in the repository.
18. Do not introduce a new database framework unless required.
19. Every generated file must contain complete content.
20. NEVER modify main.py.
21. NEVER modify backend/main.py.
22. NEVER overwrite protected infrastructure.
23. Do not create duplicate endpoints.
24. Do not create placeholder implementations.
25. Do not return explanations outside the JSON.
26. Return ONLY valid JSON.
27. Do not use markdown code fences.

CRITICAL:

Before returning the JSON, verify mentally:

- Does the production code actually implement the requirement?
- If this is an API requirement, does the endpoint become reachable?
- Is there at least one production implementation file?
- Are tests only testing functionality that actually exists?

JSON FORMAT:

{{
    "summary": "short implementation summary",
    "files": [
        {{
            "path": "relative/path/to/production/file.py",
            "action": "create",
            "content": "complete production file content"
        }},
        {{
            "path": "relative/path/to/test_file.py",
            "action": "create",
            "content": "complete pytest file content"
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

                result = self._clean_json_response(
                    result
                )

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

                self._validate_implementation(
                    files_result
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
                part in self.PROTECTED_DIRECTORIES
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