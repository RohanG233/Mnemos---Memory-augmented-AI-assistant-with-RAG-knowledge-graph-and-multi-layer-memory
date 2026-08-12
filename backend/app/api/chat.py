from fastapi import APIRouter

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from app.main import rag_service


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest
):

    result = rag_service.chat(
        request.message
    )

    return ChatResponse(
        answer=result["answer"],

        retrieved_chunks=result[
            "retrieved_chunks"
        ],

        memories=result[
            "memories"
        ],

        episodes=result[
            "episodes"
        ],

        procedures=result[
            "procedures"
        ],

        graph_facts=result[
            "graph_facts"
        ]
    )