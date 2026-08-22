from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import (
    document_collection,
    model
)

from app.graph.store import (
    load_graph
)

from app.services.llm_service import (
    LLMService
)

from app.services.document_service import (
    DocumentService
)

from app.services.rag_service import (
    RAGService
)


# --------------------------------
# Create FastAPI application
# --------------------------------

app = FastAPI(
    title="ACAi Backend",
    description=(
        "AI memory and knowledge graph "
        "RAG backend"
    ),
    version="1.0.0"
)


# --------------------------------
# CORS
# --------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------
# Load Knowledge Graph
# --------------------------------

graph = load_graph()


# --------------------------------
# LLM Service
# --------------------------------

llm_service = LLMService()


# --------------------------------
# Document Service
# --------------------------------

document_service = DocumentService(
    graph=graph,
    llm_service=llm_service
)


# --------------------------------
# RAG Service
# --------------------------------

rag_service = RAGService(
    graph=graph,

    document_service=document_service,

    llm_service=llm_service
)


# --------------------------------
# API Routers
# --------------------------------

from app.api.chat import router as chat_router
from app.api.documents import router as document_router
from app.api.memories import router as memory_router
from app.api.graph import router as graph_router
from app.api.auth import router as auth_router


app.include_router(
    auth_router
)

app.include_router(
    chat_router
)

app.include_router(
    document_router
)

app.include_router(
    memory_router
)

app.include_router(
    graph_router
)


# --------------------------------
# Health Check
# --------------------------------

@app.get("/")
def root():

    return {
        "name": "ACAi Backend",
        "status": "running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",

        "documents":
            document_collection.count(),

        "graph_nodes":
            len(graph.nodes),

        "graph_edges":
            len(graph.edges)
    }