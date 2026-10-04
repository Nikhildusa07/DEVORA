from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.test_generation_service import TestGenerationService


router = APIRouter(
    prefix="/testing",
    tags=["Testing"]
)

service = TestGenerationService()


class TestGenerationRequest(BaseModel):
    requirement: str


@router.post("/generate")
def generate_tests(request: TestGenerationRequest):
    try:
        return service.generate_tests(request.requirement)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )