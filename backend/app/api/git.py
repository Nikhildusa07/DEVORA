from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.git_service import GitService


router = APIRouter(
    prefix="/git",
    tags=["Git"]
)

service = GitService()


class GitStatusRequest(BaseModel):
    repository_path: str


@router.post("/status")
def git_status(request: GitStatusRequest):
    try:
        return service.get_status(
            request.repository_path
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
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