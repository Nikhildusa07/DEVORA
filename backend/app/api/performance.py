from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.performance_service import PerformanceService


router = APIRouter(
    prefix="/performance",
    tags=["Performance"]
)

service = PerformanceService()


class PerformanceRequest(BaseModel):
    code: str


@router.post("/analyze")
def analyze_performance(request: PerformanceRequest):
    try:
        return service.analyze(request.code)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )