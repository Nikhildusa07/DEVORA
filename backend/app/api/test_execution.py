from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.test_execution_service import TestExecutionService


router = APIRouter(
    prefix="/test-execution",
    tags=["Test Execution"]
)

service = TestExecutionService()


class TestExecutionRequest(BaseModel):
    repository_path: str


@router.post("/run")
def run_tests(request: TestExecutionRequest):
    try:
        return service.execute_tests(
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