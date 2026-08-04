import bm25s
import Stemmer

# -------------------------------
# 1. Corpus (Documents)
# -------------------------------
corpus = [
    "A cat is a feline and likes to purr.",
    "A dog is the human's best friend and loves to play.",
    "A bird is a beautiful animal that can fly.",
    "A fish is a creature that lives in water and swims.",
    "Python is a popular programming language.",
    "FAISS is used for semantic vector search.",
]

# -------------------------------
# 2. Create Stemmer
# -------------------------------
stemmer = Stemmer.Stemmer("english")

# -------------------------------
# 3. Tokenize Documents
# -------------------------------
corpus_tokens = bm25s.tokenize(
    corpus,
    stopwords="en",
    stemmer=stemmer
)

# -------------------------------
# 4. Build BM25 Index
# -------------------------------
retriever = bm25s.BM25()
retriever.index(corpus_tokens)

#print("Indexed", len(corpus), "documents")

# -------------------------------
# 5. User Query
# -------------------------------
query = "Which animal swims in water?"

query_tokens = bm25s.tokenize(
    query,
    stemmer=stemmer
)

# -------------------------------
# 6. Retrieve Top-k
# -------------------------------
results, scores = retriever.retrieve(
    query_tokens,
    k=3
)

# -------------------------------
# 7. Display Results
# -------------------------------
print(results)
# print("\nTop Results:\n")

# for rank in range(results.shape[1]):
#     print(f"Rank {rank + 1}")
#     print(f"Document : {results[0, rank]}")
#     print(f"Score    : {scores[0, rank]:.4f}")
#     print()