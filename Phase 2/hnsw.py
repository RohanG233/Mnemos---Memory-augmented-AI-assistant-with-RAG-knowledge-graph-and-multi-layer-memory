import faiss
import numpy as np

# -------------------------------
# 1. Parameters
# -------------------------------
d = 128                 # Embedding dimension
M = 32                  # Maximum neighbors

efConstruction = 40
efSearch = 16

# -------------------------------
# 2. Create HNSW Index
# -------------------------------
index = faiss.IndexHNSWFlat(d, M)

# Set graph construction parameter
index.hnsw.efConstruction = efConstruction

# -------------------------------
# 3. Document Embeddings
# -------------------------------
# In a real RAG system:
# xb = embedding_model.encode(documents).astype("float32")

xb = np.random.random((1000, d)).astype("float32")

# -------------------------------
# 4. Build HNSW Graph
# -------------------------------
index.add(xb)

# print("Indexed vectors :", index.ntotal)
# print("Entry Point     :", index.hnsw.entry_point)
# print("Max Level       :", index.hnsw.max_level)

# -------------------------------
# 5. Query Embedding
# -------------------------------
# In a real RAG system:
# xq = embedding_model.encode([query]).astype("float32")

xq = np.random.random((1, d)).astype("float32")

# -------------------------------
# 6. Search Parameter
# -------------------------------
index.hnsw.efSearch = efSearch

# -------------------------------
# 7. Search
# -------------------------------
k = 5

distances, indices = index.search(xq, k)

# -------------------------------
# 8. Display Results
# -------------------------------

hnsw_doc_ids = indices[0].tolist()
print(hnsw_doc_ids)

# print("\nNearest Neighbors:\n")

# for rank in range(k):
#     print(f"Rank {rank + 1}")
#     print(f"Document ID : {indices[0][rank]}")
#     print(f"Distance    : {distances[0][rank]:.4f}")
#     print()