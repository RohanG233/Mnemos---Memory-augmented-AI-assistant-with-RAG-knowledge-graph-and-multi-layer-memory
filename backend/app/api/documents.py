from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

import os
import tempfile

from app.main import (
    document_service
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    if not file.filename.endswith(
        ".txt"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only .txt files are supported"
        )

    content = await file.read()

    text = content.decode(
        "utf-8"
    )

    result = (
        document_service.ingest_text(
            text,
            source=file.filename
        )
    )

    return {
        "message":
            "Document uploaded successfully",

        "filename":
            file.filename,

        "chunks":
            result["chunks"]
    }