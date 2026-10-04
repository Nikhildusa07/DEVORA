from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.code_review_service import CodeReviewService


router = APIRouter(
    prefix="/code-review",
    tags=["Code Review"]
)

service = CodeReviewService()


class CodeReviewRequest(BaseModel):
    code: str


@router.post("/review")
def review_code(request: CodeReviewRequest):
    try:
        return service.review(request.code)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )