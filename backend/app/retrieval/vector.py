import logging

from app.core.config import VECTOR_TOP_K

logger = logging.getLogger(__name__)


class VectorRetriever:

    def __init__(self, collection):
        self.collection = collection


    def search(
        self,
        query_embedding,
        user_id: str,
        k: int = VECTOR_TOP_K,
    ) -> list[str]:
        """
        Perform vector similarity search against the user's
        ChromaDB documents.

        Returns
        -------
        list[str]
            Chroma document IDs (e.g. "<uuid>_chunk_0").
            These are returned as-is so they can be used
            directly to fetch document text from Chroma.
        """

        # Count only this user's documents
        try:
            user_results = self.collection.get(
                where={"user_id": user_id},
                include=[],
            )
            user_count = len(user_results["ids"])
        except Exception:
            user_count = 0

        if user_count == 0:
            return []

        actual_k = min(k, user_count)

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=actual_k,
                where={"user_id": user_id},
                include=["documents"],
            )
        except Exception:
            logger.exception("Vector search failed for user_id=%s", user_id)
            return []

        # Return the Chroma IDs (strings like "<uuid>_chunk_N")
        return results["ids"][0]
