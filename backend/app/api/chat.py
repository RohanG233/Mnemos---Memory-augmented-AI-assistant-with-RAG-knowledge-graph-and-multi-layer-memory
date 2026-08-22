from fastapi import APIRouter

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
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
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
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