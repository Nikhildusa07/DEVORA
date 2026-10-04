from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.requirement_service import RequirementService


router = APIRouter(
    prefix="/requirements",
    tags=["Requirements"]
)

service = RequirementService()


class RequirementRequest(BaseModel):
    requirement: str


@router.post("/analyze")
def analyze_requirement(request: RequirementRequest):
    try:
        return service.analyze(request.requirement)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )