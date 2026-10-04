from pathlib import Path
import ast


class ArchitectureDiscoveryService:

    IGNORED_DIRECTORIES = {
        ".git",
        "venv",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
    }

    def discover(self, repository_path: str):

        repository = Path(repository_path).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                "Repository path does not exist."
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                "Repository path is not a directory."
            )

        files = []
        python_modules = []
        classes = []
        functions = []

        for path in repository.rglob("*"):

            if any(
                part in self.IGNORED_DIRECTORIES
                for part in path.parts
            ):
                continue

            if not path.is_file():
                continue

            relative_path = str(
                path.relative_to(repository)
            )

            files.append(relative_path)

            if path.suffix != ".py":
                continue

            python_modules.append(relative_path)

            try:
                source = path.read_text(
                    encoding="utf-8"
                )

                tree = ast.parse(source)

                for node in ast.walk(tree):

                    if isinstance(node, ast.ClassDef):
                        classes.append({
                            "file": relative_path,
                            "name": node.name
                        })

                    elif isinstance(
                        node,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef
                        )
                    ):
                        functions.append({
                            "file": relative_path,
                            "name": node.name
                        })

            except (
                SyntaxError,
                UnicodeDecodeError
            ):
                continue

        return {
            "repository": str(repository),
            "total_files": len(files),
            "python_modules": python_modules,
            "classes": classes,
            "functions": functions,
            "status": "architecture_discovered",
            "next_stage": "code_modification"
        }