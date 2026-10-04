from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.architecture_service import ArchitectureService


router = APIRouter(
    prefix="/architecture",
    tags=["Architecture"]
)

service = ArchitectureService()


class ArchitectureRequest(BaseModel):
    requirement: str


@router.post("/plan")
def create_architecture_plan(request: ArchitectureRequest):
    try:
        return service.create_plan(request.requirement)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )