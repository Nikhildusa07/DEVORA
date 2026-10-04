from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.code_generation_service import CodeGenerationService


router = APIRouter(
    prefix="/code-generation",
    tags=["Code Generation"]
)

service = CodeGenerationService()


class CodeGenerationRequest(BaseModel):
    requirement: str
    implementation_plan: list


@router.post("/prepare")
def prepare_code_generation(request: CodeGenerationRequest):
    try:
        return service.generate_task(
            request.requirement,
            request.implementation_plan
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )