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
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        ".gitignore"
    }

    PROTECTED_DIRECTORIES = {
        ".git",
        "venv",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules"
    }

    FORBIDDEN_FILE_NAMES = {
        ".env",
        ".env.local",
        ".env.production",
        ".env.development"
    }

    FORBIDDEN_EXTENSIONS = {
        ".pem",
        ".key",
        ".crt",
        ".p12",
        ".pfx"
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

            relative_path = path.relative_to(
                repository
            )

            relative_string = str(
                relative_path
            ).replace(
                "\\",
                "/"
            )

            if relative_string in self.PROTECTED_FILES:
                continue

            if path.name in self.FORBIDDEN_FILE_NAMES:
                continue

            if path.suffix.lower() in self.FORBIDDEN_EXTENSIONS:
                continue

            files.append(
                relative_string
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

    def _normalize_path(
        self,
        file_path: str
    ):

        normalized_path = (
            str(file_path)
            .strip()
            .replace("\\", "/")
            .strip("/")
        )

        while "//" in normalized_path:
            normalized_path = normalized_path.replace(
                "//",
                "/"
            )

        return normalized_path

    def _is_test_file(
        self,
        file_path: str
    ):

        normalized_path = self._normalize_path(
            file_path
        )

        filename = Path(
            normalized_path
        ).name.lower()

        return (
            filename.startswith("test_")
            or filename.endswith("_test.py")
            or "/tests/" in f"/{normalized_path}/"
            or normalized_path.startswith("tests/")
        )

    def _is_protected_path(
        self,
        file_path: str
    ):

        normalized_path = self._normalize_path(
            file_path
        )

        if not normalized_path:
            return True

        if normalized_path in self.PROTECTED_FILES:
            return True

        path = Path(
            normalized_path
        )

        if any(
            part in self.PROTECTED_DIRECTORIES
            for part in path.parts
        ):
            return True

        if path.name in self.FORBIDDEN_FILE_NAMES:
            return True

        if path.suffix.lower() in self.FORBIDDEN_EXTENSIONS:
            return True

        return False

    def _detect_test_import_target(
        self,
        repository: Path
    ):

        backend_main = repository / "backend" / "main.py"

        root_main = repository / "main.py"

        app_main = repository / "app" / "main.py"

        if backend_main.exists():

            return {
                "module": "main",
                "working_directory": "backend",
                "entrypoint": "backend/main.py"
            }

        if root_main.exists():

            return {
                "module": "main",
                "working_directory": ".",
                "entrypoint": "main.py"
            }

        if app_main.exists():

            return {
                "module": "app.main",
                "working_directory": ".",
                "entrypoint": "app/main.py"
            }

        return {
            "module": None,
            "working_directory": ".",
            "entrypoint": None
        }

    def _normalize_generated_test_imports(
        self,
        repository: Path,
        files_result: list
    ):

        import_target = self._detect_test_import_target(
            repository
        )

        module = import_target.get(
            "module"
        )

        if not module:
            return files_result

        normalized_files = []

        for file_data in files_result:

            if not isinstance(
                file_data,
                dict
            ):
                normalized_files.append(
                    file_data
                )
                continue

            copied_file = dict(
                file_data
            )

            path = self._normalize_path(
                str(
                    copied_file.get(
                        "path",
                        ""
                    )
                )
            )

            content = copied_file.get(
                "content",
                ""
            )

            if (
                self._is_test_file(path)
                and isinstance(content, str)
            ):

                if import_target["entrypoint"] == "backend/main.py":

                    replacements = {
                        "from backend.main import app":
                            "from main import app",

                        "from backend.main import":
                            "from main import",

                        "import backend.main":
                            "import main"
                    }

                    for old, new in replacements.items():

                        content = content.replace(
                            old,
                            new
                        )

                elif import_target["entrypoint"] == "main.py":

                    replacements = {
                        "from backend.main import app":
                            "from main import app",

                        "from backend.main import":
                            "from main import",

                        "import backend.main":
                            "import main"
                    }

                    for old, new in replacements.items():

                        content = content.replace(
                            old,
                            new
                        )

                copied_file["content"] = content

            normalized_files.append(
                copied_file
            )

        return normalized_files

    def _validate_implementation(
        self,
        files_result: list,
        requirement: str
    ):

        if not files_result:
            raise ValueError(
                "AI generated no implementation files."
            )

        production_files = []
        test_files = []

        normalized_paths = set()

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

            normalized_path = self._normalize_path(
                path
            )

            if not normalized_path:
                raise ValueError(
                    "Implementation contains an invalid file path."
                )

            if normalized_path in normalized_paths:
                raise ValueError(
                    f"Duplicate implementation path: "
                    f"{normalized_path}"
                )

            normalized_paths.add(
                normalized_path
            )

            if self._is_protected_path(
                normalized_path
            ):
                raise ValueError(
                    f"AI attempted to modify a protected path: "
                    f"{normalized_path}"
                )

            action = str(
                file_data.get(
                    "action",
                    "create"
                )
            ).strip().lower()

            if action not in {
                "create",
                "modify"
            }:
                raise ValueError(
                    f"Unsupported file action: {action}"
                )

            content = file_data.get(
                "content",
                ""
            )

            if not isinstance(
                content,
                str
            ):
                raise ValueError(
                    f"File content must be a string: "
                    f"{normalized_path}"
                )

            if not content.strip():
                raise ValueError(
                    f"Generated file is empty: "
                    f"{normalized_path}"
                )

            if self._is_test_file(
                normalized_path
            ):

                test_files.append(
                    normalized_path
                )

            else:

                production_files.append(
                    normalized_path
                )

        if not production_files:
            raise ValueError(
                "AI generated tests without production "
                "implementation. A real production "
                "implementation is required."
            )

        requirement_lower = requirement.lower()

        api_keywords = [
            "api",
            "endpoint",
            "route",
            "rest",
            "get endpoint",
            "post endpoint",
            "put endpoint",
            "delete endpoint"
        ]

        is_api_requirement = any(
            keyword in requirement_lower
            for keyword in api_keywords
        )

        if is_api_requirement:

            production_python_files = [
                path
                for path in production_files
                if path.lower().endswith(".py")
            ]

            if not production_python_files:
                raise ValueError(
                    "API requirement did not produce "
                    "a Python production implementation."
                )

        return {
            "production_files": production_files,
            "test_files": test_files
        }

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

        repository_files = "\n".join(
            files
        )

        import_target = self._detect_test_import_target(
            repository
        )

        test_module = import_target.get(
            "module"
        )

        test_working_directory = import_target.get(
            "working_directory"
        )

        test_entrypoint = import_target.get(
            "entrypoint"
        )

        prompt = f"""
You are DEVORA, an autonomous AI
software engineering implementation engine.

Your job is to implement the user's requirement
inside the EXISTING repository.

You are NOT a test-generation-only system.

You must create the REAL production implementation
that makes the requested feature work.

REQUIREMENT:
{requirement}

AI REASONING:
{reasoning}

EXISTING REPOSITORY FILES:
{repository_files}

==================================================
TEST EXECUTION ENVIRONMENT
==================================================

Detected application entrypoint:
{test_entrypoint}

Detected test working directory:
{test_working_directory}

Detected Python application import module:
{test_module}

IMPORTANT:

Tests will be executed according to the repository's
actual backend/test execution structure.

If the application entrypoint is:

backend/main.py

and tests are executed from:

backend/

then the correct import is:

from main import app

NOT:

from backend.main import app

NEVER blindly use:

from backend.main import app

when the test execution working directory is backend/.

The generated test MUST use an import that actually
works from the detected test execution directory.

==================================================
IMPLEMENTATION RULES
==================================================

1. You MUST implement the actual production feature.

2. Tests are supplementary.
   Tests MUST NEVER replace production implementation.

3. NEVER return only test files.

4. Every requested feature must have corresponding
   production code.

5. Inspect the existing repository structure before
   deciding where implementation belongs.

6. Preserve the existing architecture.

7. Reuse existing routers, services, models,
   schemas and utilities whenever appropriate.

8. Do not create duplicate functionality when an
   appropriate existing module already exists.

9. If the requirement asks for an API endpoint:

   - create or modify the appropriate production API module;
   - implement the endpoint completely;
   - use the existing FastAPI architecture;
   - use the existing router structure;
   - register the router if a new router is created;
   - if direct route registration is required,
     modify the application's actual entrypoint;
   - the endpoint MUST be reachable by the running
     FastAPI application;
   - do NOT merely create a test;
   - do NOT create an unused router;
   - do NOT create an unregistered API module.

10. If backend/main.py is the application's FastAPI
    entrypoint and route registration is required,
    YOU MAY MODIFY backend/main.py.

11. If main.py is the application's FastAPI
    entrypoint and route registration is required,
    YOU MAY MODIFY main.py.

12. When modifying an existing file, return the
    COMPLETE updated file content.

13. Never return partial file content.

14. Never use placeholder content.

15. Every generated file must contain complete,
    runnable content.

16. If a new production module is required,
    create it completely.

17. Generate pytest tests AFTER production
    implementation.

18. Tests MUST test functionality that actually exists.

19. Never generate tests for functionality that
    has not been implemented.

20. API tests MUST use the exact route implemented
    by production code.

21. Do not guess multiple random API paths.

22. Do not create duplicate endpoint aliases unless
    explicitly required.

23. Never delete existing files.

24. Never modify .env files.

25. Never modify secrets.

26. Never generate API keys, passwords or credentials.

27. Never modify .git configuration.

28. Never modify virtual environments.

29. Never modify node_modules.

30. Never modify protected directories.

31. Use technologies already present in the repository.

32. Do not introduce a new framework when the existing
    framework satisfies the requirement.

33. Do not introduce a new database framework unless
    explicitly required.

34. Do not replace the application's architecture
    merely to implement a small feature.

35. Preserve existing working functionality.

36. Do not remove existing endpoints.

37. Do not remove existing routers.

38. Do not overwrite unrelated functionality.

39. Do not create unrelated files.

40. Do not create placeholder implementations.

41. Return ONLY valid JSON.

42. Do not use markdown code fences.

==================================================
API VERIFICATION
==================================================

Before returning JSON, verify:

A. Production implementation exists.

B. API route is defined.

C. Route is connected to FastAPI.

D. Router is registered if necessary.

E. Endpoint is reachable.

F. Test uses the actual endpoint path.

G. Test imports the application using the actual
   detected execution environment.

H. Existing routes remain intact.

I. No test-only implementation exists.

If any answer is NO, fix the implementation first.

==================================================
ENTRYPOINT RULE
==================================================

Determine the real application entrypoint.

Possible entrypoints include:

main.py
backend/main.py
app/main.py

Do NOT assume.

When modifying the entrypoint:

- preserve existing imports;
- preserve existing routers;
- preserve existing middleware;
- preserve startup behavior;
- preserve application configuration;
- add only the required functionality;
- return the COMPLETE file.

==================================================
TEST IMPORT RULE
==================================================

The test MUST import the application using the
detected execution environment.

Detected module:

{test_module}

If the detected module is:

main

the test must use:

from main import app

If the detected module is:

app.main

the test must use:

from app.main import app

Do not use:

from backend.main import app

unless backend is actually an importable package
from the test execution directory.

==================================================
FINAL SELF-CHECK
==================================================

Before returning JSON:

- Production implementation exists.
- Requested feature exists.
- API route is reachable.
- Router registration exists if required.
- Existing routes remain intact.
- Existing architecture remains intact.
- Tests correspond to real implementation.
- Tests use correct import paths.
- Tests use actual endpoint paths.
- No test-only implementation exists.
- No protected files are modified.
- No secrets are created.
- Every generated file is complete.
- No placeholder content exists.
- No duplicate endpoint was created.

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

                files_result = (
                    self._normalize_generated_test_imports(
                        repository,
                        files_result
                    )
                )

                validation = (
                    self._validate_implementation(
                        files_result,
                        requirement
                    )
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
                    "production_files": validation[
                        "production_files"
                    ],
                    "test_files": validation[
                        "test_files"
                    ],
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
            raise ValueError(
                "No implementation files were generated."
            )

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

            normalized_path = self._normalize_path(
                file_path
            )

            if not normalized_path:
                raise ValueError(
                    "Implementation contains "
                    "an invalid file path."
                )

            if self._is_protected_path(
                normalized_path
            ):
                raise ValueError(
                    f"Implementation cannot modify "
                    f"protected path: {normalized_path}"
                )

            if action not in {
                "create",
                "modify"
            }:
                raise ValueError(
                    f"Unsupported file action: {action}"
                )

            if not isinstance(
                content,
                str
            ):
                raise ValueError(
                    "File content must be a string."
                )

            if not content.strip():
                raise ValueError(
                    f"Generated file is empty: "
                    f"{normalized_path}"
                )

            target_file = (
                repository / normalized_path
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

            if target_file.name in self.FORBIDDEN_FILE_NAMES:

                raise ValueError(
                    "Implementation cannot modify "
                    "environment files."
                )

            if target_file.suffix.lower() in self.FORBIDDEN_EXTENSIONS:

                raise ValueError(
                    "Implementation cannot modify "
                    "private key or certificate files."
                )

            if (
                target_file.exists()
                and action == "create"
            ):

                raise ValueError(
                    f"Cannot create an existing file: "
                    f"{normalized_path}. "
                    f"Use action='modify' instead."
                )

            if (
                target_file.exists()
                and not target_file.is_file()
            ):

                raise ValueError(
                    f"Target path is not a file: "
                    f"{normalized_path}"
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
                ).replace(
                    "\\",
                    "/"
                )
            )

        if not changed_files:
            raise ValueError(
                "No production changes were applied."
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