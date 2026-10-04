from pathlib import Path


class RepositoryAnalyzer:

    IGNORED_DIRECTORIES = {
        ".git",
        "venv",
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
    }

    def analyze(self, repository_path: str):
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError("Repository path does not exist.")

        if not root.is_dir():
            raise NotADirectoryError("Provided path is not a directory.")

        files = []
        directories = []

        for path in root.rglob("*"):
            if any(part in self.IGNORED_DIRECTORIES for part in path.parts):
                continue

            if path.is_dir():
                directories.append(str(path.relative_to(root)))

            elif path.is_file():
                files.append({
                    "name": path.name,
                    "path": str(path.relative_to(root)),
                    "extension": path.suffix or "no_extension"
                })

        return {
            "repository": root.resolve().name,
            "path": str(root.resolve()),
            "total_files": len(files),
            "total_directories": len(directories),
            "files": files,
            "directories": directories,
        }