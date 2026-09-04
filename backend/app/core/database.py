import logging
import os

import numpy as np
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from pymongo import MongoClient

from app.core.config import (
    CHROMA_PATH,
    MONGODB_URL,
    MONGODB_DATABASE,
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------
# ChromaDB
# -------------------------------------------------------

os.makedirs(CHROMA_PATH, exist_ok=True)
logger.info("Initialising ChromaDB at path: %s", CHROMA_PATH)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)


# -------------------------------------------------------
# Embedding function
#
# ONNXMiniLM_L6_V2 ships inside chromadb itself.
# It runs all-MiniLM-L6-v2 via onnxruntime — same model,
# same 384-dim vectors, zero extra packages, ~80 MB RAM.
# No PyTorch. No sentence-transformers. Works on Render free tier.
# -------------------------------------------------------

embedding_function = ONNXMiniLM_L6_V2()

logger.info("ChromaDB: using ONNXMiniLM_L6_V2 embedding function (~80 MB, no PyTorch).")


# -------------------------------------------------------
# Lightweight model wrapper
#
# rag_service.py and maintenance.py call model.encode(text)
# and expect a numpy array back.
# We wrap ONNXMiniLM_L6_V2 to provide that interface.
# -------------------------------------------------------

class _OnnxEmbedder:
    """
    Thin wrapper around ONNXMiniLM_L6_V2 that exposes
    the same .encode(text) → np.ndarray interface that
    the rest of the codebase expects.
    """

    def __init__(self, fn):
        self._fn = fn

    def encode(self, text):
        """
        text: str  → returns np.ndarray shape (384,)
        text: list → returns np.ndarray shape (N, 384)
        """
        single = isinstance(text, str)
        inputs = [text] if single else list(text)
        vectors = self._fn(inputs)          # returns list[list[float]]
        arr = np.array(vectors, dtype=np.float32)
        return arr[0] if single else arr


model = _OnnxEmbedder(embedding_function)

logger.info("Embedding model wrapper ready.")


# -------------------------------------------------------
# Chroma Collections
# -------------------------------------------------------

document_collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_function,
)

memory_collection = chroma_client.get_or_create_collection(
    name="memory",
    embedding_function=embedding_function,
)

episode_collection = chroma_client.get_or_create_collection(
    name="episodes",
    embedding_function=embedding_function,
)

procedure_collection = chroma_client.get_or_create_collection(
    name="procedures",
    embedding_function=embedding_function,
)

logger.info("ChromaDB collections ready.")


# -------------------------------------------------------
# MongoDB
# -------------------------------------------------------

logger.info("Connecting to MongoDB…")

mongo_client = MongoClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=10_000,
)

mongo_database           = mongo_client[MONGODB_DATABASE]
users_collection         = mongo_database["users"]
conversations_collection = mongo_database["conversations"]
messages_collection      = mongo_database["messages"]

try:
    mongo_client.admin.command("ping")
    logger.info("MongoDB connection OK (database=%s).", MONGODB_DATABASE)

    users_collection.create_index("google_id", unique=True)
    users_collection.create_index("refresh_token", sparse=True)

    conversations_collection.create_index(
        [("user_id", 1), ("updated_at", -1)]
    )
    conversations_collection.create_index("conversation_id", unique=True)

    messages_collection.create_index(
        [("conversation_id", 1), ("created_at", 1)]
    )
    messages_collection.create_index("user_id")

    logger.info("MongoDB indexes ensured.")

except Exception:
    logger.exception(
        "MongoDB connectivity check failed. "
        "Check MONGODB_URL and network access."
    )
