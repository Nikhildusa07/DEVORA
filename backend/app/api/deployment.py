from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.deployment_service import DeploymentService


router = APIRouter(
    prefix="/deployment",
    tags=["Deployment"]
)

service = DeploymentService()


class DeploymentRequest(BaseModel):
    repository_path: str


@router.post("/check")
def check_deployment(request: DeploymentRequest):
    try:
        return service.check_readiness(
            request.repository_path
        )

    except (
        FileNotFoundError,
        NotADirectoryError
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