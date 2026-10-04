from pathlib import Path


class PullRequestService:

    def generate_pull_request(
        self,
        repository_path: str,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str
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

        title = title.strip()
        description = description.strip()
        source_branch = source_branch.strip()
        target_branch = target_branch.strip()

        if not title:
            raise ValueError(
                "Pull request title cannot be empty."
            )

        if not source_branch:
            raise ValueError(
                "Source branch cannot be empty."
            )

        if not target_branch:
            raise ValueError(
                "Target branch cannot be empty."
            )

        return {
            "repository": str(repository),
            "pull_request": {
                "title": title,
                "description": description,
                "source_branch": source_branch,
                "target_branch": target_branch
            },
            "status": "pull_request_generated",
            "message": (
                "Pull request definition generated successfully."
            ),
            "next_stage": "ci_cd"
        }