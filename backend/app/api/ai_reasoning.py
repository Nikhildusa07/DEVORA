from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai_reasoning_service import (
    AIReasoningService
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Reasoning"]
)


class AIReasoningRequest(BaseModel):

    requirement: str
    repository_context: str = ""


@router.post("/reason")
def reason_about_requirement(
    request: AIReasoningRequest
):

    try:

        service = AIReasoningService()

        return service.reason(
            request.requirement,
            request.repository_context
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