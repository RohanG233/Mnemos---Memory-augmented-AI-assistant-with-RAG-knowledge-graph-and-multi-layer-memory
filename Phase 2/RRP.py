import bm25s
import Stemmer
import faiss
import numpy as np
from collections import defaultdict

# ======================================================
# 1. Documents
# ======================================================

documents = [
    "A cat is a feline and likes to purr.",
    "A dog is the human's best friend and loves to play.",
    "A bird is a beautiful animal that can fly.",
    "A fish is a creature that lives in water and swims.",
    "Python is a popular programming language.",
    "FAISS is used for semantic vector search."
]

# ======================================================
# 2. BM25
# ======================================================

stemmer = Stemmer.Stemmer("english")

corpus_tokens = bm25s.tokenize(
    documents,
    stopwords="en",
    stemmer=stemmer
)

bm25 = bm25s.BM25()
bm25.index(corpus_tokens)

query = "Which animal swims in water?"

query_tokens = bm25s.tokenize(
    query,
    stemmer=stemmer
)

bm25_results, bm25_scores = bm25.retrieve(
    query_tokens,
    k=3         
)

bm25_doc_ids = bm25_results[0].tolist()

print("BM25 Ranking")
print(bm25_doc_ids)

# ======================================================
# 3. HNSW
# ======================================================

d = 128
M = 32

index = faiss.IndexHNSWFlat(d, M)

index.hnsw.efConstruction = 40

# In a real RAG:
# xb = embedding_model.encode(documents).astype("float32")

xb = np.random.random((len(documents), d)).astype("float32")

index.add(xb)

# In a real RAG:
# xq = embedding_model.encode([query]).astype("float32")

xq = np.random.random((1, d)).astype("float32")

index.hnsw.efSearch = 16

distances, indices = index.search(xq, k=3)

hnsw_doc_ids = indices[0].tolist()

print("\nHNSW Ranking")
print(hnsw_doc_ids)

# ======================================================
# 4. Reciprocal Rank Fusion
# ======================================================

def reciprocal_rank_fusion(rankings, k=60):
    scores = defaultdict(float)

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1 / (k + rank)

    return sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

rrf_results = reciprocal_rank_fusion(
    [bm25_doc_ids, hnsw_doc_ids]
)

print("\nRRF Ranking")
print(rrf_results)

# ======================================================
# 5. Final Documents
# ======================================================

print("\nFinal Retrieved Documents\n")

for doc_id, score in rrf_results:
    print(f"Doc ID : {doc_id}")
    print(f"RRF Score : {score:.5f}")
    print(documents[doc_id])
    print("-" * 50)