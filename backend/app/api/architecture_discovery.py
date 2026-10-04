from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.architecture_discovery_service import (
    ArchitectureDiscoveryService
)


router = APIRouter(
    prefix="/architecture",
    tags=["Architecture"]
)

service = ArchitectureDiscoveryService()


class ArchitectureDiscoveryRequest(BaseModel):
    repository_path: str


@router.post("/discover")
def discover_architecture(
    request: ArchitectureDiscoveryRequest
):

    try:
        return service.discover(
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