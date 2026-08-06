import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime


class SemanticMemoryRetriever:
    def __init__(self):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.memory_store = []
        self.embeddings = []

    def store_memory(self, message, context):
        """Store message with its semantic embedding."""
        embedding = self.encoder.encode(message)

        self.memory_store.append({
            "message": message,
            "context": context,
            "timestamp": datetime.now()
        })

        self.embeddings.append(embedding)

    def retrieve_relevant_memories(self, query, top_k=5):
        """Retrieve the most semantically similar memories."""

        if len(self.memory_store) == 0:
            return []

        query_embedding = self.encoder.encode(query)

        similarities = []

        for emb in self.embeddings:
            similarity = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) *
                np.linalg.norm(emb)
            )
            similarities.append(similarity)

        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [self.memory_store[i] for i in top_indices]


# ----------------------------
# Example
# ----------------------------

memory = SemanticMemoryRetriever()

memory.store_memory(
    "I love playing football.",
    "User preference"
)

memory.store_memory(
    "My favorite language is Python.",
    "Programming"
)

memory.store_memory(
    "I live in Bangalore.",
    "Personal"
)

results = memory.retrieve_relevant_memories(
    "What sports do I like?"
)

for item in results:
    print(item)