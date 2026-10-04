from pathlib import Path
import ast


class DependencyService:

    def analyze(self, repository_path: str):

        repository = Path(repository_path).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                "Repository path does not exist."
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                "Repository path is not a directory."
            )

        dependencies = set()

        for python_file in repository.rglob("*.py"):

            if any(
                part in {
                    "venv",
                    ".venv",
                    "__pycache__",
                    ".git"
                }
                for part in python_file.parts
            ):
                continue

            try:
                source = python_file.read_text(
                    encoding="utf-8"
                )

                tree = ast.parse(source)

                for node in ast.walk(tree):

                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies.add(
                                alias.name.split(".")[0]
                            )

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies.add(
                                node.module.split(".")[0]
                            )

            except (SyntaxError, UnicodeDecodeError):
                continue

        dependencies = sorted(dependencies)

        return {
            "repository": str(repository),
            "dependencies": dependencies,
            "total_dependencies": len(dependencies),
            "status": "dependency_analysis_completed",
            "next_stage": "architecture_discovery"
        }   