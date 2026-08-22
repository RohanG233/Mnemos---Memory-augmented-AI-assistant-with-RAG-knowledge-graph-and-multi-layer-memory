import os

from dotenv import load_dotenv


load_dotenv()


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


# -----------------------------
# Authentication Configuration
# -----------------------------

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017"
)

MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "acai"
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "15"
    )
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv(
        "REFRESH_TOKEN_EXPIRE_DAYS",
        "7"
    )
)


# -----------------------------
# Google OAuth Configuration
# -----------------------------

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID"
)

GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET"
)

GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/auth/google/callback"
)

GOOGLE_AUTHORIZATION_URL = (
    "https://accounts.google.com/o/oauth2/auth"
)

GOOGLE_TOKEN_URL = (
    "https://oauth2.googleapis.com/token"
)

GOOGLE_USER_INFO_URL = (
    "https://www.googleapis.com/oauth2/v2/userinfo"
)

GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]