from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.debugging_service import DebuggingService


router = APIRouter(
    prefix="/debugging",
    tags=["Debugging"]
)

service = DebuggingService()


class DebuggingRequest(BaseModel):
    test_output: str
    test_error: str = ""


@router.post("/diagnose")
def diagnose_failure(request: DebuggingRequest):
    try:
        return service.diagnose(
            request.test_output,
            request.test_error
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )