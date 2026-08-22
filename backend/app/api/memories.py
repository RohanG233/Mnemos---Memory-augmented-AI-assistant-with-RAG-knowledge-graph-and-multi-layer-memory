from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user

from app.core.database import (
    memory_collection,
    episode_collection,
    procedure_collection
)


router = APIRouter(
    prefix="/memories",
    tags=["Memories"]
)


@router.get("")
def get_memories(user_id: str = Depends(get_current_user)):

    results = memory_collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    return {
        "count":
            len(results["ids"]),

        "memories": [
            {
                "id": memory_id,
                "content": document,
                "metadata": metadata
            }

            for memory_id, document, metadata
            in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ]
    }


@router.get("/episodes")
def get_episodes(user_id: str = Depends(get_current_user)):

    results = episode_collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    return {
        "count":
            len(results["ids"]),

        "episodes": [
            {
                "id": episode_id,
                "content": document,
                "metadata": metadata
            }

            for episode_id, document, metadata
            in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ]
    }


@router.get("/procedures")
def get_procedures(user_id: str = Depends(get_current_user)):

    results = procedure_collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    return {
        "count":
            len(results["ids"]),

        "procedures": [
            {
                "id": procedure_id,
                "content": document,
                "metadata": metadata
            }

            for procedure_id, document, metadata
            in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ]
    }