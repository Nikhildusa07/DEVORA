import json
from datetime import datetime
from pathlib import Path


class RepositoryMemoryService:

    MEMORY_FILE = ".devora_repository_memory.json"

    def save_memory(
        self,
        repository_path: str,
        memory_type: str,
        content: dict
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

        memory_type = memory_type.strip()

        if not memory_type:
            raise ValueError(
                "Memory type cannot be empty."
            )

        memory_path = repository / self.MEMORY_FILE

        if memory_path.exists():

            try:
                memory = json.loads(
                    memory_path.read_text(
                        encoding="utf-8"
                    )
                )

            except json.JSONDecodeError:

                memory = {
                    "repository": str(repository),
                    "memories": []
                }

        else:

            memory = {
                "repository": str(repository),
                "memories": []
            }

        memory["memories"].append({
            "type": memory_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        memory_path.write_text(
            json.dumps(
                memory,
                indent=4
            ),
            encoding="utf-8"
        )

        return {
            "repository": str(repository),
            "memory_type": memory_type,
            "total_memories": len(
                memory["memories"]
            ),
            "status": "memory_stored",
            "message": (
                "Repository memory stored successfully."
            ),
            "next_stage": "autonomous_workflow"
        }

    def get_memory(
        self,
        repository_path: str
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

        memory_path = repository / self.MEMORY_FILE

        if not memory_path.exists():

            return {
                "repository": str(repository),
                "memories": [],
                "total_memories": 0,
                "status": "memory_empty"
            }

        try:

            memory = json.loads(
                memory_path.read_text(
                    encoding="utf-8"
                )
            )

        except json.JSONDecodeError:

            memory = {
                "repository": str(repository),
                "memories": []
            }

        return {
            "repository": str(repository),
            "memories": memory.get(
                "memories",
                []
            ),
            "total_memories": len(
                memory.get(
                    "memories",
                    []
                )
            ),
            "status": "memory_retrieved"
        }