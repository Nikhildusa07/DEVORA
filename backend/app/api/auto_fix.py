from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.auto_fix_service import AutoFixService


router = APIRouter(
    prefix="/debugging",
    tags=["Debugging"]
)

service = AutoFixService()


class AutoFixRequest(BaseModel):
    test_output: str
    test_error: str = ""


@router.post("/auto-fix")
def analyze_auto_fix(
    request: AutoFixRequest
):

    try:
        return service.generate_fix(
            request.test_output,
            request.test_error
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )