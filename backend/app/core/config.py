import os


# -----------------------------
# LLM Configuration
# -----------------------------

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest"
)


# -----------------------------
# Storage Configuration
# -----------------------------

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "./data/chroma_db"
)

GRAPH_PATH = os.getenv(
    "GRAPH_PATH",
    "./data/graph.json"
)


# -----------------------------
# RAG Configuration
# -----------------------------

CHUNK_SIZE = 500
CHUNK_OVERLAP = 70

BM25_TOP_K = 5
VECTOR_TOP_K = 5
FINAL_TOP_K = 5

RRF_K = 60


# -----------------------------
# Conversation Configuration
# -----------------------------

SHORT_TERM_MESSAGES = 6


# -----------------------------
# Memory Configuration
# -----------------------------

MEMORY_RETRIEVAL_TOP_K = 3

MEMORY_SIMILARITY_THRESHOLD = 0.20

MEMORY_FORGET_THRESHOLD = 0.15