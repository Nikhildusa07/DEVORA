from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.dependency_service import DependencyService


router = APIRouter(
    prefix="/dependencies",
    tags=["Dependencies"]
)

service = DependencyService()


class DependencyRequest(BaseModel):
    repository_path: str


@router.post("/analyze")
def analyze_dependencies(request: DependencyRequest):

    try:
        return service.analyze(
            request.repository_path
        )

    except (
        FileNotFoundError,
        NotADirectoryError
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