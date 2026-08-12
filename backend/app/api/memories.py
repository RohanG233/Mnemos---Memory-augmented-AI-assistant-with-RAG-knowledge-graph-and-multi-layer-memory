from fastapi import APIRouter

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
def get_memories():

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
def get_episodes():

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
def get_procedures():

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