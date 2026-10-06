from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.autonomous_workflow_service import (
    AutonomousWorkflowService
)


router = APIRouter(
    prefix="/autonomous",
    tags=["Autonomous Workflow"]
)

service = AutonomousWorkflowService()


class AutonomousWorkflowRequest(BaseModel):

    repository_path: str
    requirement: str
    code: str


@router.post("/execute")
def execute_workflow(
    request: AutonomousWorkflowRequest
):

    try:

        return service.execute(
            request.requirement,
            request.code,
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