from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.git_commit_service import GitCommitService


router = APIRouter(
    prefix="/git",
    tags=["Git"]
)

service = GitCommitService()


class GitCommitRequest(BaseModel):
    repository_path: str
    message: str


@router.post("/commit")
def commit_changes(request: GitCommitRequest):
    try:
        return service.commit_changes(
            request.repository_path,
            request.message
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError,
        RuntimeError
    ) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )