from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.repository_analyzer import RepositoryAnalyzer


router = APIRouter(prefix="/repository", tags=["Repository"])

analyzer = RepositoryAnalyzer()


class RepositoryRequest(BaseModel):
    path: str


@router.post("/analyze")
def analyze_repository(request: RepositoryRequest):
    try:
        result = analyzer.analyze(request.path)
        return result

    except (FileNotFoundError, NotADirectoryError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )