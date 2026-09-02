import logging

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.core.database import (
    episode_collection,
    memory_collection,
    procedure_collection,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memories", tags=["Memories"])


@router.get("")
def get_memories(
    user_id: str = Depends(get_current_user),
):
    results = memory_collection.get(
        where={"user_id": user_id},
        include=["documents", "metadatas"],
    )

    return {
        "count": len(results["ids"]),
        "memories": [
            {"id": mid, "content": doc, "metadata": meta}
            for mid, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"],
            )
        ],
    }


@router.get("/episodes")
def get_episodes(
    user_id: str = Depends(get_current_user),
):
    results = episode_collection.get(
        where={"user_id": user_id},
        include=["documents", "metadatas"],
    )

    return {
        "count": len(results["ids"]),
        "episodes": [
            {"id": eid, "content": doc, "metadata": meta}
            for eid, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"],
            )
        ],
    }


@router.get("/procedures")
def get_procedures(
    user_id: str = Depends(get_current_user),
):
    results = procedure_collection.get(
        where={"user_id": user_id},
        include=["documents", "metadatas"],
    )

    return {
        "count": len(results["ids"]),
        "procedures": [
            {"id": pid, "content": doc, "metadata": meta}
            for pid, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"],
            )
        ],
    }
