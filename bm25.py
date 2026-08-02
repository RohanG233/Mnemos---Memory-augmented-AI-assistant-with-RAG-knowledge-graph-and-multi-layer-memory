documents = [
    "The cat sat on the mat",
    "Dogs chase cats",
    "The cat likes fish"
]

tokenized_docs = [doc.lower().split() for doc in documents]

# print(tokenized_docs)

from rank_bm25 import BM25Okapi

bm25 = BM25Okapi(tokenized_docs)

query = "cat fish"
tokenized_query = query.lower().split()

scores = bm25.get_scores(tokenized_query)
# print(scores)

ranked = sorted(
    zip(documents, scores),
    key=lambda x: x[1],
    reverse=True
)

for doc, score in ranked:
    print(f"{score:.2f} -> {doc}")