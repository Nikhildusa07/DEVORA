from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rollback_service import (
    RollbackService
)


router = APIRouter(
    prefix="/rollback",
    tags=["Automatic Rollback"]
)

service = RollbackService()


class RollbackRequest(BaseModel):
    repository_path: str
    commit: str = "HEAD~1"


@router.post("/execute")
def execute_rollback(
    request: RollbackRequest
):

    try:
        return service.rollback(
            request.repository_path,
            request.commit
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