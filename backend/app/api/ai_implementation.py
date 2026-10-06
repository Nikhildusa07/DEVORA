from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai_implementation_service import (
    AIImplementationService
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Implementation"]
)

service = AIImplementationService()


class AIImplementationRequest(BaseModel):

    repository_path: str
    requirement: str
    reasoning: str


class ApplyImplementationRequest(BaseModel):

    repository_path: str
    implementation: dict


@router.post("/generate-implementation")
def generate_implementation(
    request: AIImplementationRequest
):

    try:

        return service.generate_implementation(
            request.requirement,
            request.reasoning,
            request.repository_path
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError
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


@router.post("/apply-implementation")
def apply_implementation(
    request: ApplyImplementationRequest
):

    try:

        return service.apply_changes(
            request.repository_path,
            request.implementation
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError
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