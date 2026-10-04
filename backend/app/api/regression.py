from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.regression_service import (
    RegressionService
)


router = APIRouter(
    prefix="/regression",
    tags=["Regression Detection"]
)

service = RegressionService()


class RegressionRequest(BaseModel):
    repository_path: str
    current_return_code: int
    current_output: str = ""


@router.post("/analyze")
def analyze_regression(
    request: RegressionRequest
):

    try:
        return service.analyze(
            request.repository_path,
            request.current_return_code,
            request.current_output
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