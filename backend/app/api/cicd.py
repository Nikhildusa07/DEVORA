from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.cicd_service import CICDService


router = APIRouter(
    prefix="/cicd",
    tags=["CI/CD"]
)

service = CICDService()


class CICDRequest(BaseModel):
    repository_path: str


@router.post("/analyze")
def analyze_cicd(request: CICDRequest):

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