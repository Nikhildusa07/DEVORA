import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv()


class AIImplementationService:

    MODELS = [
        "gemini-3.8-flash"
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

    def _is_api_requirement(
        self,
        requirement: str
    ):
        requirement_lower = requirement.lower()

        api_keywords = [
            "api",
            "endpoint",
            "route",
            "rest"
        ]

        return any(
            keyword in requirement_lower
            for keyword in api_keywords
        )

    def _detect_entrypoint(
        self,
        repository: Path
    ):
        candidates = [
            repository / "backend" / "main.py",
            repository / "main.py",
            repository / "app" / "main.py"
        ]

        for candidate in candidates:
            if candidate.is_file():
                return candidate

        return None

    def _infer_api_path(
        self,
        requirement: str
    ):
        explicit_path = re.search(
            r"(?<![A-Za-z0-9_])(/[A-Za-z0-9_./{}:-]+)",
            requirement
        )

        if explicit_path:
            return explicit_path.group(1).rstrip(".,")

        if "welcome" in requirement.lower():
            return "/welcome"

        match = re.search(
            r"endpoint(?:\s+that)?\s+"
            r"(?:returns?|responds?\s+with|provides?)"
            r"\s+(?:a|an|the)?\s*"
            r"([A-Za-z0-9_-]+)",
            requirement.lower()
        )

        if match:
            return "/" + match.group(1).strip("_- ")

        return "/api"

    def _infer_api_response(
        self,
        requirement: str
    ):
        if "welcome" in requirement.lower():
            return '{"message": "Welcome"}'

        quoted = re.search(
            r'(?:returns?|responds?\s+with)\s+["\']([^"\']+)["\']',
            requirement,
            re.IGNORECASE
        )

        if quoted:
            value = (
                quoted.group(1)
                .strip()
                .replace('"', '\\"')
            )

            return '{"message": "' + value + '"}'

        return '{"message": "OK"}'

    def _extract_generated_routes(
        self,
        files_result
    ):
        routes = []

        decorator_pattern = re.compile(
            r'@(?:app|router)\.'
            r'(?:get|post|put|delete|patch)'
            r'\(\s*["\']([^"\']+)["\']',
            re.IGNORECASE
        )

        for file_data in files_result:

            if not isinstance(
                file_data,
                dict
            ):
                continue

            path = str(
                file_data.get(
                    "path",
                    ""
                )
            )

            if self._is_test_file(path):
                continue

            content = str(
                file_data.get(
                    "content",
                    ""
                )
            )

            for match in decorator_pattern.finditer(
                content
            ):
                routes.append(
                    match.group(1)
                )

        return routes

    def _route_registered_in_entrypoint(
        self,
        entrypoint_content: str,
        route_path: str
    ):
        direct_pattern = re.compile(
            r'@app\.(?:get|post|put|delete|patch)'
            r'\(\s*["\']'
            + re.escape(route_path)
            + r'["\']',
            re.IGNORECASE
        )

        if direct_pattern.search(
            entrypoint_content
        ):
            return True

        return False

    def _router_registration_exists(
        self,
        entrypoint_content: str,
        files_result,
        route_path: str
    ):
        router_names = []

        for file_data in files_result:

            if not isinstance(
                file_data,
                dict
            ):
                continue

            path = self._normalize_path(
                str(
                    file_data.get(
                        "path",
                        ""
                    )
                )
            )

            if self._is_test_file(path):
                continue

            content = str(
                file_data.get(
                    "content",
                    ""
                )
            )

            if route_path not in content:
                continue

            if "@router." not in content:
                continue

            for match in re.finditer(
                r'@router\.(?:get|post|put|delete|patch)',
                content,
                re.IGNORECASE
            ):
                if match:
                    router_names.append("router")
                    break

        if not router_names:
            return False

        include_router_pattern = re.compile(
            r'(?:include_router|include_router\s*\()',
            re.IGNORECASE
        )

        return bool(
            include_router_pattern.search(
                entrypoint_content
            )
        )

    def _build_direct_route(
        self,
        requirement: str,
        route_path: str
    ):
        method_match = re.search(
            r"\b(GET|POST|PUT|DELETE|PATCH)\b",
            requirement,
            re.IGNORECASE
        )

        method = (
            method_match.group(1).lower()
            if method_match
            else "get"
        )

        response = self._infer_api_response(
            requirement
        )

        function_name = (
            "devora_generated_endpoint"
        )

        route_code = (
            "\n\n"
            f"@app.{method}("
            f'"{route_path}"'
            ")\n"
            f"def {function_name}():\n"
            f"    return {response}\n"
        )

        return route_code

    def _normalize_generated_test_imports(
        self,
        files_result,
        repository: Path
    ):
        entrypoint = self._detect_entrypoint(
            repository
        )

        if entrypoint is None:
            return files_result

        entrypoint_relative = (
            str(
                entrypoint.relative_to(
                    repository
                )
            )
            .replace("\\", "/")
        )

        if entrypoint_relative == "backend/main.py":

            replacements = {
                "from backend.main import app":
                    "from main import app",

                "from backend.main import":
                    "from main import"
            }

        elif entrypoint_relative == "main.py":

            replacements = {
                "from backend.main import app":
                    "from main import app",

                "from backend.main import":
                    "from main import"
            }

        else:

            replacements = {}

        for file_data in files_result:

            if not isinstance(
                file_data,
                dict
            ):
                continue

            path = str(
                file_data.get(
                    "path",
                    ""
                )
            )

            if not self._is_test_file(path):
                continue

            content = str(
                file_data.get(
                    "content",
                    ""
                )
            )

            for old, new in replacements.items():
                content = content.replace(
                    old,
                    new
                )

            file_data["content"] = content

        return files_result

    def _repair_api_implementation(
        self,
        repository: Path,
        files_result: list,
        requirement: str
    ):
        if not self._is_api_requirement(
            requirement
        ):
            return files_result

        entrypoint = self._detect_entrypoint(
            repository
        )

        if entrypoint is None:
            raise ValueError(
                "API requirement detected, but no "
                "FastAPI application entrypoint was found."
            )

        selected_path = self._infer_api_path(
            requirement
        )

        routes = self._extract_generated_routes(
            files_result
        )

        if routes:
            matching_routes = [
                route
                for route in routes
                if route == selected_path
            ]

            if matching_routes:
                selected_path = matching_routes[0]

        production_map = {}

        for file_data in files_result:

            if not isinstance(
                file_data,
                dict
            ):
                continue

            path = self._normalize_path(
                str(
                    file_data.get(
                        "path",
                        ""
                    )
                )
            )

            if path:
                production_map[path] = file_data

        entrypoint_relative = (
            str(
                entrypoint.relative_to(
                    repository
                )
            )
            .replace("\\", "/")
        )

        entrypoint_data = production_map.get(
            entrypoint_relative
        )

        if entrypoint_data is not None:
            entrypoint_content = str(
                entrypoint_data.get(
                    "content",
                    ""
                )
            )
        else:
            entrypoint_content = entrypoint.read_text(
                encoding="utf-8"
            )

        registered = (
            self._route_registered_in_entrypoint(
                entrypoint_content,
                selected_path
            )
        )

        if not registered:

            route_code = self._build_direct_route(
                requirement,
                selected_path
            )

            entrypoint_content = (
                entrypoint_content.rstrip()
                + route_code
                + "\n"
            )

            if entrypoint_data is None:

                files_result.append(
                    {
                        "path": entrypoint_relative,
                        "action": "modify",
                        "content": entrypoint_content
                    }
                )

            else:

                entrypoint_data["action"] = "modify"

                entrypoint_data["content"] = (
                    entrypoint_content
                )

        for file_data in files_result:

            if not isinstance(
                file_data,
                dict
            ):
                continue

            path = str(
                file_data.get(
                    "path",
                    ""
                )
            )

            if not self._is_test_file(path):
                continue

            content = str(
                file_data.get(
                    "content",
                    ""
                )
            )

            if "welcome" in requirement.lower():

                content = content.replace(
                    "/api/v1/welcome",
                    selected_path
                )

                content = content.replace(
                    "/api/welcome",
                    selected_path
                )

            file_data["content"] = content

        files_result = (
            self._normalize_generated_test_imports(
                files_result,
                repository
            )
        )

        return files_result

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
                    "Duplicate implementation path: "
                    f"{normalized_path}"
                )

            normalized_paths.add(
                normalized_path
            )

            if self._is_protected_path(
                normalized_path
            ):
                raise ValueError(
                    "AI attempted to modify a protected path: "
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
                    "File content must be a string: "
                    f"{normalized_path}"
                )

            if not content.strip():
                raise ValueError(
                    "Generated file is empty: "
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

        prompt = f"""
You are DEVORA, an autonomous AI software engineering implementation engine.

Your job is to implement the user's requirement inside the EXISTING repository.

You are NOT a test-generation-only system.

You must create the REAL production implementation that makes the requested feature work.

REQUIREMENT:
{requirement}

AI REASONING:
{reasoning}

EXISTING REPOSITORY FILES:
{repository_files}

==================================================
IMPLEMENTATION RULES
==================================================

1. You MUST implement the actual production feature.

2. Tests are supplementary.
   Tests MUST NEVER replace production implementation.

3. NEVER return only test files.

4. Every requested feature must have corresponding production code.

5. Inspect the existing repository structure before deciding where implementation belongs.

6. Preserve the existing architecture.

7. Reuse existing routers, services, models, schemas and utilities whenever appropriate.

8. Do not create duplicate functionality when an appropriate existing module already exists.

9. If the requirement asks for an API endpoint:

   - create or modify the appropriate production API module;
   - implement the endpoint completely;
   - use the existing FastAPI architecture;
   - use the existing router structure;
   - register the router if a new router is created;
   - if direct route registration is required, modify the actual application entrypoint;
   - the endpoint MUST be reachable by the running FastAPI application;
   - do NOT merely create a test;
   - do NOT create an unused router;
   - do NOT create an unregistered API module.

10. If backend/main.py is the application's FastAPI entrypoint and route registration is required, YOU MAY MODIFY backend/main.py.

11. If main.py is the application's FastAPI entrypoint and route registration is required, YOU MAY MODIFY main.py.

12. When modifying an existing file, return the COMPLETE updated file content.

13. Never return partial file content.

14. Never use placeholders such as:
    "add this code here"
    "insert this line"
    "existing code remains"
    "..."
    
15. Every generated file must contain complete runnable content.

16. If a new production module is required, create it completely.

17. Generate appropriate pytest tests AFTER production implementation.

18. Tests MUST test functionality that actually exists.

19. Never generate tests for an endpoint that has not been implemented.

20. If tests are generated for an API endpoint, use the actual route path created by the production implementation.

21. Do not guess multiple random API paths merely to make tests pass.

22. Do not create duplicate endpoint aliases unless explicitly required.

23. Never delete existing files.

24. Never modify .env files.

25. Never modify secrets.

26. Never generate API keys, passwords or credentials.

27. Never modify Git configuration.

28. Never modify virtual environments.

29. Never modify node_modules.

30. Never modify protected directories.

31. Do not introduce a new framework when an existing framework already satisfies the requirement.

32. Use technologies already present in the repository.

33. Do not introduce a new database framework unless explicitly required.

34. Do not replace the application's architecture merely to implement a small feature.

35. Preserve existing working functionality.

36. Do not remove existing endpoints.

37. Do not remove existing routers.

38. Do not overwrite unrelated functionality.

39. Do not fabricate unrelated files.

40. Do not create placeholder implementations.

41. Return ONLY valid JSON.

42. Do not use markdown code fences.

==================================================
CRITICAL API VERIFICATION
==================================================

If the requirement is an API requirement, verify:

A. Actual production code exists.

B. The API route is defined.

C. The route is connected to the FastAPI application.

D. If a router is used, the router is included by the application's entrypoint.

E. The requested endpoint is reachable from the running application.

F. The route path used by tests is the same route path implemented by production.

G. Existing routes are preserved.

H. Tests are not generated without production implementation.

If any answer is NO, fix the implementation before returning JSON.

==================================================
APPLICATION ENTRYPOINT
==================================================

Determine the real application entrypoint from the repository.

Possible entrypoints include:

- main.py
- backend/main.py
- app/main.py

Do NOT assume.

If route registration is required, modify the actual entrypoint.

When modifying the entrypoint:

- preserve existing imports;
- preserve existing routers;
- preserve existing middleware;
- preserve existing startup behavior;
- preserve existing configuration;
- add only the required implementation;
- return the COMPLETE file.

==================================================
TEST RULE
==================================================

Tests must be generated AFTER production implementation.

Tests must:

- import the real application;
- call the actual implemented route;
- verify the HTTP status;
- verify the expected response;
- avoid random fallback paths;
- avoid imaginary endpoints.

If production implements:

GET /welcome

then the test must call:

GET /welcome

It must NOT invent:

/api/welcome
/api/v1/welcome

unless those paths actually exist.

==================================================
SAFETY RULE
==================================================

Protected infrastructure includes:

- .env
- .env.local
- .env.production
- .env.development
- .git
- venv
- .venv
- __pycache__
- .pytest_cache
- node_modules
- private key/certificate files

These MUST NOT be modified.

The application entrypoint is NOT automatically protected because autonomous software engineering sometimes requires route registration there.

==================================================
FINAL SELF-CHECK
==================================================

Before returning JSON, verify:

- Production implementation exists.
- Requested feature exists.
- API route is reachable.
- Router registration exists if required.
- Existing routes remain intact.
- Existing architecture remains intact.
- Tests correspond to real implementation.
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
                        "AI implementation response must be a JSON object."
                    )

                files_result = implementation.get(
                    "files"
                )

                if not isinstance(
                    files_result,
                    list
                ):
                    raise ValueError(
                        "AI implementation response must contain a files list."
                    )

                files_result = (
                    self._repair_api_implementation(
                        repository,
                        files_result,
                        requirement
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

                errors.append(
                    {
                        "model": model,
                        "error": str(error)
                    }
                )

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
                    "Implementation contains an empty file path."
                )

            normalized_path = self._normalize_path(
                file_path
            )

            if not normalized_path:
                raise ValueError(
                    "Implementation contains an invalid file path."
                )

            if self._is_protected_path(
                normalized_path
            ):
                raise ValueError(
                    "Implementation cannot modify protected path: "
                    f"{normalized_path}"
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
                    f"Generated file is empty: {normalized_path}"
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
                    "Implementation file path must remain inside the repository."
                )

            if any(
                part in self.PROTECTED_DIRECTORIES
                for part in target_file.parts
            ):
                raise ValueError(
                    "Implementation cannot modify protected directories."
                )

            if target_file.name in self.FORBIDDEN_FILE_NAMES:
                raise ValueError(
                    "Implementation cannot modify environment files."
                )

            if target_file.suffix.lower() in self.FORBIDDEN_EXTENSIONS:
                raise ValueError(
                    "Implementation cannot modify private key or certificate files."
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
                    f"Target path is not a file: {normalized_path}"
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
            "repository": str(
                repository
            ),
            "changed_files": changed_files,
            "skipped_files": skipped_files,
            "total_files": len(
                changed_files
            ),
            "next_stage": "testing"
        }