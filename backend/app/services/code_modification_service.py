from pathlib import Path


class CodeModificationService:

    def modify_file(
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

        file_path = file_path.strip()

        if not file_path:
            raise ValueError(
                "File path cannot be empty."
            )

        target_file = (
            repository / file_path
        ).resolve()

        try:
            target_file.relative_to(repository)
        except ValueError:
            raise ValueError(
                "File path must remain inside the repository."
            )

        if not target_file.exists():
            raise FileNotFoundError(
                "Target file does not exist."
            )

        if not target_file.is_file():
            raise ValueError(
                "Target path is not a file."
            )

        target_file.write_text(
            content,
            encoding="utf-8"
        )

        return {
            "repository": str(repository),
            "file": str(
                target_file.relative_to(repository)
            ),
            "status": "file_modified",
            "message": "Existing file modified successfully.",
            "next_stage": "testing"
        }