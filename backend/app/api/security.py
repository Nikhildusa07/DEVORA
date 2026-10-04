from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.security_service import SecurityService


router = APIRouter(
    prefix="/security",
    tags=["Security"]
)

service = SecurityService()


class SecurityRequest(BaseModel):
    code: str


@router.post("/analyze")
def analyze_security(request: SecurityRequest):
    try:
        return service.analyze(request.code)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )