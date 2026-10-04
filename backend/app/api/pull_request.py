from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.pull_request_service import PullRequestService


router = APIRouter(
    prefix="/git",
    tags=["Git"]
)

service = PullRequestService()


class PullRequestRequest(BaseModel):
    repository_path: str
    title: str
    description: str = ""
    source_branch: str
    target_branch: str


@router.post("/pull-request")
def generate_pull_request(
    request: PullRequestRequest
):

    try:
        return service.generate_pull_request(
            request.repository_path,
            request.title,
            request.description,
            request.source_branch,
            request.target_branch
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError
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