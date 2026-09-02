import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import (
    ALLOWED_ORIGINS,
    validate_required_env_vars,
)

# Configure logging before anything else
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger(__name__)


# --------------------------------
# Application state container
# --------------------------------

class AppState:
    llm_service = None
    document_service = None
    chat_service = None
    rag_service = None


app_state = AppState()


# --------------------------------
# Lifespan (replaces on_event)
# --------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Run startup logic, yield to serve requests,
    then run shutdown logic.
    """

    # --- Validate required env vars ---
    validate_required_env_vars()

    logger.info("Starting ACAI backend…")

    # --- Import heavy services here to
    #     keep startup order explicit ---
    from app.services.llm_service import LLMService
    from app.services.document_service import DocumentService
    from app.services.chat_service import ChatService
    from app.services.rag_service import RAGService

    app_state.llm_service = LLMService()

    app_state.document_service = DocumentService(
        llm_service=app_state.llm_service
    )

    app_state.chat_service = ChatService()

    app_state.rag_service = RAGService(
        document_service=app_state.document_service,
        llm_service=app_state.llm_service,
    )

    # Rebuild BM25 indexes from existing Chroma data
    try:
        app_state.document_service.initialize()
        logger.info("BM25 indexes rebuilt from existing documents.")
    except Exception:
        logger.exception(
            "Non-fatal: BM25 initialization failed. "
            "Documents may not be searchable until re-indexed."
        )

    # Ensure graph directory exists
    try:
        import os
        from app.core.config import GRAPH_DIRECTORY
        os.makedirs(GRAPH_DIRECTORY, exist_ok=True)
        logger.info("Graph directory ready: %s", GRAPH_DIRECTORY)
    except Exception:
        logger.exception("Could not create graph directory.")

    logger.info("ACAI backend started. Serving requests.")

    yield

    # --- Shutdown ---
    logger.info("ACAI backend shutting down.")


# --------------------------------
# Create FastAPI application
# --------------------------------

app = FastAPI(
    title="ACAI Backend",
    description="AI memory and knowledge graph RAG backend",
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------
# CORS
# --------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS origins: %s", ALLOWED_ORIGINS)


# --------------------------------
# API Routers
# --------------------------------

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.documents import router as document_router
from app.api.memories import router as memory_router
from app.api.graph import router as graph_router

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(document_router)
app.include_router(memory_router)
app.include_router(graph_router)


# --------------------------------
# Health Check
# --------------------------------

@app.get("/")
def root():
    return {"name": "ACAI Backend", "status": "running"}


@app.get("/health")
def health():
    """
    Basic liveness probe.
    Returns 200 when the process is alive.
    Does not test LLM or database connectivity
    so it never fails due to external services.
    """
    return {"status": "healthy"}


@app.get("/health/dependencies")
def health_dependencies():
    """
    Diagnostic endpoint.
    Checks MongoDB and Ollama reachability.
    Do not expose publicly in production.
    """
    import requests
    from app.core.config import OLLAMA_URL, LLM_TIMEOUT
    from app.core.database import mongo_client

    result: dict = {}

    # MongoDB
    try:
        mongo_client.admin.command("ping")
        result["mongodb"] = "ok"
    except Exception as exc:
        result["mongodb"] = f"error: {exc}"

    # Ollama — only check the base URL
    ollama_base = OLLAMA_URL.split("/api")[0]
    try:
        r = requests.get(
            f"{ollama_base}/api/tags",
            timeout=5,
        )
        result["ollama"] = "ok" if r.ok else f"http {r.status_code}"
    except Exception as exc:
        result["ollama"] = f"error: {exc}"

    return result
