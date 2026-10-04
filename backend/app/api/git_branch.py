from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.git_branch_service import GitBranchService


router = APIRouter(
    prefix="/git",
    tags=["Git"]
)

service = GitBranchService()


class GitBranchRequest(BaseModel):
    repository_path: str
    branch_name: str


@router.post("/branch")
def create_branch(request: GitBranchRequest):

    try:
        return service.create_branch(
            request.repository_path,
            request.branch_name
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