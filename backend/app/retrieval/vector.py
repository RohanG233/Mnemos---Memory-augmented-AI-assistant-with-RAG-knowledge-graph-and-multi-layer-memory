from app.core.config import VECTOR_TOP_K


class VectorRetriever:

    def __init__(self, collection):
        self.collection = collection


    def search(
        self,
        query_embedding,
        k=VECTOR_TOP_K
    ):
        """
        Perform vector similarity search
        against the ChromaDB document collection.
        """

        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=min(
                k,
                self.collection.count()
            )
        )

        vector_doc_ids = [
            int(doc_id.split("_")[1])
            for doc_id in results["ids"][0]
        ]

        return vector_doc_ids