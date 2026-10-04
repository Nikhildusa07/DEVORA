from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.refactoring_service import (
    RefactoringService
)


router = APIRouter(
    prefix="/refactoring",
    tags=["Refactoring"]
)

service = RefactoringService()


class RefactoringRequest(BaseModel):
    repository_path: str
    file_path: str


@router.post("/analyze")
def analyze_refactoring(
    request: RefactoringRequest
):

    try:
        return service.analyze(
            request.repository_path,
            request.file_path
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