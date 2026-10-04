from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.implementation_service import ImplementationService


router = APIRouter(
    prefix="/implementation",
    tags=["Implementation"]
)

service = ImplementationService()


class ImplementationRequest(BaseModel):
    repository_path: str
    file_path: str
    content: str


@router.post("/create-file")
def create_file(request: ImplementationRequest):
    try:
        return service.implement_file(
            request.repository_path,
            request.file_path,
            request.content
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