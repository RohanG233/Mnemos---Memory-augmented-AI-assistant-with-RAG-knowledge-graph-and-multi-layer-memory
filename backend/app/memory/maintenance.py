import math
import time

from app.core.config import (
    MEMORY_FORGET_THRESHOLD,
    MEMORY_RETRIEVAL_TOP_K
)


def maintain_memories(
    collection
):
    """
    Apply memory decay and remove memories
    whose memory strength falls below the
    configured threshold.
    """

    now = time.time()

    results = collection.get(
        include=["metadatas"]
    )

    ids = results["ids"]
    metadatas = results["metadatas"]

    for memory_id, metadata in zip(
        ids,
        metadatas
    ):

        importance = metadata.get(
            "importance",
            0.5
        )

        last_accessed = metadata.get(
            "last_accessed",
            now
        )

        access_count = metadata.get(
            "access_count",
            0
        )

        age_days = (
            now - last_accessed
        ) / 86400

        # Recency decay
        recency = math.exp(
            -0.05 * age_days
        )

        # Usage reinforcement
        usage = min(
            1.0,
            math.log1p(
                access_count
            ) / 5
        )

        # Final memory strength
        score = (
            0.5 * importance
            + 0.3 * recency
            + 0.2 * usage
        )

        if score < MEMORY_FORGET_THRESHOLD:

            collection.delete(
                ids=[memory_id]
            )

        else:

            collection.update(
                ids=[memory_id],
                metadatas=[
                    {
                        **metadata,
                        "memory_score": score
                    }
                ]
            )


def reinforce_memories(
    collection,
    query_embedding,
    n_results=MEMORY_RETRIEVAL_TOP_K
):
    """
    Retrieve memories semantically and
    reinforce their access statistics.
    """

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=min(
            n_results,
            collection.count()
        )
    )

    retrieved_documents = (
        results["documents"][0]
    )

    memory_ids = (
        results["ids"][0]
    )

    now = time.time()

    for memory_id in memory_ids:

        memory_data = collection.get(
            ids=[memory_id],
            include=["metadatas"]
        )

        metadata = (
            memory_data["metadatas"][0]
        )

        access_count = metadata.get(
            "access_count",
            0
        )

        collection.update(
            ids=[memory_id],
            metadatas=[
                {
                    **metadata,
                    "access_count":
                        access_count + 1,
                    "last_accessed":
                        now
                }
            ]
        )

    return retrieved_documents


def find_similar_memory(
    collection,
    embedding_model,
    text,
    threshold=0.20
):
    """
    Find the most semantically similar
    existing memory.
    """

    if collection.count() == 0:
        return None

    embedding = embedding_model.encode(
        text
    )

    results = collection.query(
        query_embeddings=[
            embedding.tolist()
        ],
        n_results=1,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    if not results["ids"][0]:
        return None

    distance = (
        results["distances"][0][0]
    )

    if distance <= threshold:

        return {
            "id": results["ids"][0][0],
            "document":
                results["documents"][0][0],
            "metadata":
                results["metadatas"][0],
            "distance":
                distance
        }

    return None