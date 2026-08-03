from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the parking area.",
]

embeddings = model.encode(sentences)
print(embeddings.shape)


# 3. Calculate the embedding similarities
similarities = model.similarity(embeddings, embeddings)
print(similarities)
