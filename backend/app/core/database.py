import chromadb

from pymongo import MongoClient

from sentence_transformers import SentenceTransformer

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

from app.core.config import (
    CHROMA_PATH,
    MONGODB_URL,
    MONGODB_DATABASE,
)


# -----------------------------
# ChromaDB
# -----------------------------

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# -----------------------------
# Embedding Function
# -----------------------------

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


# -----------------------------
# Sentence Transformer Model
# -----------------------------

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# -----------------------------
# Chroma Collections
# -----------------------------

document_collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_function
)


memory_collection = chroma_client.get_or_create_collection(
    name="memory",
    embedding_function=embedding_function
)


episode_collection = chroma_client.get_or_create_collection(
    name="episodes",
    embedding_function=embedding_function
)


procedure_collection = chroma_client.get_or_create_collection(
    name="procedures",
    embedding_function=embedding_function
)


# -----------------------------
# MongoDB
# -----------------------------

mongo_client = MongoClient(
    MONGODB_URL
)

mongo_database = mongo_client[
    MONGODB_DATABASE
]

users_collection = mongo_database[
    "users"
]


# -----------------------------
# User Index
# -----------------------------

users_collection.create_index(
    "google_id",
    unique=True
)