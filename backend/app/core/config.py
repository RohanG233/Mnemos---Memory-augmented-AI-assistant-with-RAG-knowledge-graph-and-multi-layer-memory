import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend directory (where this file lives),
# not from the working directory — prevents path mismatch when
# uvicorn is started from a parent directory.
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

logger = logging.getLogger(__name__)


# -----------------------------
# Project root — used to resolve
# relative storage paths safely
# -----------------------------

# This is the backend/ directory regardless of working directory
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def _resolve_path(env_value: str, default_relative: str) -> str:
    """
    Return an absolute path.
    - If the env var is already absolute, use it as-is.
    - If it's relative (e.g. './data/chroma_db'), resolve it
      from the backend/ directory so it is stable regardless
      of where uvicorn is launched from.
    """
    raw = env_value or default_relative
    p = Path(raw)
    if p.is_absolute():
        return str(p)
    return str((_BACKEND_DIR / raw).resolve())


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

LLM_TIMEOUT = int(
    os.getenv("LLM_TIMEOUT", "120")
)


# -----------------------------
# Storage Configuration
# -----------------------------

CHROMA_PATH = _resolve_path(
    os.getenv("CHROMA_PATH", ""),
    "data/chroma_db"
)

GRAPH_DIRECTORY = _resolve_path(
    os.getenv("GRAPH_DIRECTORY", ""),
    "data/graphs"
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

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "mnemos")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)


# -----------------------------
# Google OAuth Configuration
# -----------------------------

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/auth/google/callback"
)

# Where the browser is redirected after OAuth completes
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# -----------------------------
# CORS
# -----------------------------

# Comma-separated list of allowed origins.
# e.g. "http://localhost:5173,https://mnemos.example.com"
_cors_raw = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
)

ALLOWED_ORIGINS: list[str] = [
    origin.strip()
    for origin in _cors_raw.split(",")
    if origin.strip()
]


# -----------------------------
# Required variable validation
# -----------------------------

def validate_required_env_vars() -> None:
    """
    Fail fast at startup if critical
    environment variables are missing.
    Only enforced when not running in
    a local-dev default context.
    """

    errors: list[str] = []

    if not JWT_SECRET_KEY:
        errors.append(
            "JWT_SECRET_KEY is not set. "
            "Generate a strong secret and set it."
        )

    if not GOOGLE_CLIENT_ID:
        errors.append(
            "GOOGLE_CLIENT_ID is not set."
        )

    if not GOOGLE_CLIENT_SECRET:
        errors.append(
            "GOOGLE_CLIENT_SECRET is not set."
        )

    if errors:
        for message in errors:
            logger.critical("MISSING ENV VAR: %s", message)

        sys.exit(
            "Startup aborted — required environment variables are missing.\n"
            + "\n".join(errors)
        )
