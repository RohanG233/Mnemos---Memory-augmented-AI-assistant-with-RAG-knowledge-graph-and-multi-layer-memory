import logging
import math
import time

from app.core.config import (
    MEMORY_FORGET_THRESHOLD,
    MEMORY_RETRIEVAL_TOP_K,
)

logger = logging.getLogger(__name__)


def maintain_memories(collection) -> None:
    """
    Apply memory decay and remove memories whose
    memory strength falls below the configured threshold.
    """

    now = time.time()

    results = collection.get(include=["metadatas"])

    ids = results["ids"]
    metadatas = results["metadatas"]

    for memory_id, metadata in zip(ids, metadatas):
        importance = metadata.get("importance", 0.5)
        last_accessed = metadata.get("last_accessed", now)
        access_count = metadata.get("access_count", 0)

        age_days = (now - last_accessed) / 86400

        recency = math.exp(-0.05 * age_days)
        usage = min(1.0, math.log1p(access_count) / 5)
        score = 0.5 * importance + 0.3 * recency + 0.2 * usage

        try:
            if score < MEMORY_FORGET_THRESHOLD:
                collection.delete(ids=[memory_id])
            else:
                collection.update(
                    ids=[memory_id],
                    metadatas=[{**metadata, "memory_score": score}],
                )
        except Exception:
            logger.exception("Failed to update/delete memory id=%s", memory_id)


def reinforce_memories(
    collection,
    query_embedding,
    user_id: str,
    n_results: int = MEMORY_RETRIEVAL_TOP_K,
) -> list[str]:
    """
    Retrieve memories semantically and reinforce access statistics.
    Returns a list of document strings (may be empty).
    """

    try:
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            where={"user_id": user_id},
            n_results=n_results,
            include=["documents", "metadatas"],
        )
    except Exception:
        logger.exception(
            "reinforce_memories query failed for user=%s", user_id
        )
        return []

    ids_list = results.get("ids", [[]])[0]
    docs_list = results.get("documents", [[]])[0]

    if not ids_list:
        return []

    now = time.time()

    for memory_id in ids_list:
        try:
            memory_data = collection.get(ids=[memory_id], include=["metadatas"])
            if not memory_data["metadatas"]:
                continue
            metadata = memory_data["metadatas"][0]
            access_count = metadata.get("access_count", 0)
            collection.update(
                ids=[memory_id],
                metadatas=[{
                    **metadata,
                    "access_count": access_count + 1,
                    "last_accessed": now,
                }],
            )
        except Exception:
            logger.exception("Failed to reinforce memory id=%s", memory_id)

    return docs_list


def find_similar_memory(
    collection,
    embedding_model,
    text: str,
    user_id: str,
    threshold: float = 0.20,
) -> dict | None:
    """
    Find the most semantically similar existing memory.
    Returns None when no memory is close enough.
    """

    embedding = embedding_model.encode(text)

    try:
        results = collection.query(
            query_embeddings=[embedding.tolist()],
            where={"user_id": user_id},
            n_results=1,
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        logger.exception(
            "find_similar_memory query failed for user=%s", user_id
        )
        return None

    ids = results.get("ids", [[]])[0]

    if not ids:
        return None

    distance = results["distances"][0][0]

    if distance <= threshold:
        return {
            "id": ids[0],
            "document": results["documents"][0][0],
            "metadata": results["metadatas"][0],
            "distance": distance,
        }

    return None
