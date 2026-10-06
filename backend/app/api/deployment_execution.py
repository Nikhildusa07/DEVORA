from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.deployment_execution_service import (
    DeploymentExecutionService
)


router = APIRouter(
    prefix="/deployment",
    tags=["Deployment"]
)

service = DeploymentExecutionService()


class DeploymentExecutionRequest(BaseModel):
    repository_path: str
    command: str


@router.post("/execute")
def execute_deployment(
    request: DeploymentExecutionRequest
):

    try:

        return service.deploy(
            request.repository_path,
            request.command
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