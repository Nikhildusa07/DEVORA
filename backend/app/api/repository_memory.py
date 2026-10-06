from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.repository_memory_service import (
    RepositoryMemoryService
)


router = APIRouter(
    prefix="/memory",
    tags=["Repository Memory"]
)

service = RepositoryMemoryService()


class MemoryRequest(BaseModel):
    repository_path: str
    memory_type: str
    content: dict


class MemoryReadRequest(BaseModel):
    repository_path: str


@router.post("/save")
def save_memory(
    request: MemoryRequest
):

    try:

        return service.save_memory(
            request.repository_path,
            request.memory_type,
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


@router.post("/read")
def read_memory(
    request: MemoryReadRequest
):

    try:

        return service.get_memory(
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