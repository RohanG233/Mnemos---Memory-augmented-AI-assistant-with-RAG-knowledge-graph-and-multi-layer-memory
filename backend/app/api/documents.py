import logging
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth.dependencies import get_current_user
from app.core.database import document_collection
from app.main import app_state

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

# 10 MB upload limit
_MAX_FILE_SIZE = 10 * 1024 * 1024
_ALLOWED_EXTENSIONS = {".txt"}


def _safe_filename(filename: str) -> str:
    """
    Strip directory components and dangerous characters
    to prevent path traversal.
    """
    # Take only the base name
    basename = os.path.basename(filename)
    # Remove any remaining path separators
    basename = basename.replace("/", "").replace("\\", "").replace("..", "")
    return basename or "upload.txt"


@router.get("")
def get_documents(
    user_id: str = Depends(get_current_user),
):
    results = document_collection.get(
        where={"user_id": user_id},
        include=["metadatas"],
    )

    documents: dict = {}
    for metadata in results["metadatas"]:
        doc_id = metadata.get("document_id")
        if not doc_id:
            continue
        if doc_id not in documents:
            documents[doc_id] = {
                "document_id": doc_id,
                "filename": metadata.get("source", "unknown"),
                "chunks": 0,
            }
        documents[doc_id]["chunks"] += 1

    return {"documents": list(documents.values())}


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user),
):
    document_service = app_state.document_service

    deleted = document_service.delete_document(
        document_id=document_id,
        user_id=user_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    document_service = app_state.document_service

    # --- Filename validation ---
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    safe_name = _safe_filename(file.filename)
    _, ext = os.path.splitext(safe_name.lower())

    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(_ALLOWED_EXTENSIONS)} files are supported.",
        )

    # --- Read content ---
    content = await file.read()

    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {_MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    if not content.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # --- Decode ---
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File could not be decoded as UTF-8.",
        )

    # --- Ingest ---
    try:
        result = document_service.ingest_text(
            text,
            source=safe_name,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Document ingestion failed for user=%s", user_id)
        raise HTTPException(status_code=500, detail="Document ingestion failed.")

    return {
        "message": "Document uploaded successfully",
        "document_id": result["document_id"],
        "filename": safe_name,
        "chunks": result["chunks"],
    }
