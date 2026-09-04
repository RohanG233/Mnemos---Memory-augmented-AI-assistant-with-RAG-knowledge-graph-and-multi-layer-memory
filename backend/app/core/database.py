import logging
import os

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

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
# Embedding function for ChromaDB collections
# Uses sentence-transformers/all-MiniLM-L6-v2 locally
# -------------------------------------------------------

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

logger.info("ChromaDB: using SentenceTransformer embedding function (all-MiniLM-L6-v2)")


# -------------------------------------------------------
# Sentence Transformer model
# Used directly for .encode() calls in rag_service.py
# and maintenance.py
# -------------------------------------------------------

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

logger.info("SentenceTransformer model loaded.")


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
