from pathlib import Path


class ImplementationService:

    def implement_file(
        self,
        repository_path: str,
        file_path: str,
        content: str
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

        target_file = (repository / file_path).resolve()

        try:
            target_file.relative_to(repository)
        except ValueError:
            raise ValueError(
                "File path must remain inside the repository."
            )

        target_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        target_file.write_text(
            content,
            encoding="utf-8"
        )

        return {
            "repository": str(repository),
            "file": str(target_file.relative_to(repository)),
            "status": "implemented",
            "message": "File created successfully."
        }