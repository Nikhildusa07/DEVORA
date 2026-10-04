from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.code_modification_service import (
    CodeModificationService
)


router = APIRouter(
    prefix="/code-modification",
    tags=["Code Modification"]
)

service = CodeModificationService()


class CodeModificationRequest(BaseModel):
    repository_path: str
    file_path: str
    content: str


@router.put("/modify-file")
def modify_file(
    request: CodeModificationRequest
):

    try:
        return service.modify_file(
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