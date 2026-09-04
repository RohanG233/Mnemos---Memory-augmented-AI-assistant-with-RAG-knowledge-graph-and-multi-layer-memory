import logging

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.main import app_state
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMUnavailableError, LLMModelNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


# --------------------------------
# Create Conversation
# --------------------------------

@router.post("/conversations")
def create_conversation(
    user_id: str = Depends(get_current_user),
):
    """
    Create a new conversation and return its server-assigned ID.
    The frontend must use this ID for subsequent chat requests.
    """
    chat_service = app_state.chat_service

    conversation = chat_service.create_conversation(user_id=user_id)

    return {
        "conversation_id": conversation["conversation_id"],
        "title": conversation["title"],
        "created_at": conversation["created_at"].isoformat(),
        "updated_at": conversation["updated_at"].isoformat(),
    }


# --------------------------------
# List Conversations
# --------------------------------

@router.get("/conversations")
def list_conversations(
    user_id: str = Depends(get_current_user),
):
    chat_service = app_state.chat_service
    conversations = chat_service.get_conversations(user_id=user_id)
    return {"conversations": conversations}


# --------------------------------
# Get Conversation Messages
# --------------------------------

@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
):
    chat_service = app_state.chat_service
    messages = chat_service.get_messages(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if messages is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"messages": messages}


# --------------------------------
# Rename Conversation
# --------------------------------

@router.patch("/conversations/{conversation_id}")
def rename_conversation(
    conversation_id: str,
    body: dict,
    user_id: str = Depends(get_current_user),
):
    chat_service = app_state.chat_service
    title = (body.get("title") or "").strip()

    if not title:
        raise HTTPException(status_code=400, detail="Title is required.")

    updated = chat_service.rename_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        title=title,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation renamed"}


# --------------------------------
# Delete Conversation
# --------------------------------

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
):
    chat_service = app_state.chat_service
    deleted = chat_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted"}


# --------------------------------
# Send Message (main chat endpoint)
# --------------------------------

@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Process a chat message.

    The frontend must provide a valid `conversation_id` that was
    previously returned by POST /chat/conversations.
    """

    chat_service = app_state.chat_service
    rag_service = app_state.rag_service

    # Verify the conversation exists and belongs to this user
    messages = chat_service.get_messages(
        conversation_id=request.conversation_id,
        user_id=user_id,
    )

    if messages is None:
        logger.warning(
            "Conversation not found — conversation_id=%s user_id=%s",
            request.conversation_id,
            user_id,
        )
        raise HTTPException(
            status_code=404,
            detail="Conversation not found or does not belong to you.",
        )

    # Persist user message
    chat_service.add_message(
        conversation_id=request.conversation_id,
        user_id=user_id,
        role="user",
        content=request.message,
    )

    # RAG pipeline
    try:
        result = rag_service.chat(request.message, user_id=user_id)
    except LLMUnavailableError as exc:
        logger.error("LLM unavailable for user=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=503,
            detail="The AI model is currently unavailable. Please try again later.",
        )
    except LLMModelNotFoundError as exc:
        logger.error("LLM model not found for user=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=503,
            detail="The AI model is not configured correctly on the server.",
        )
    except Exception:
        logger.exception("Unexpected error during chat for user=%s", user_id)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your message.",
        )

    # Persist assistant response
    chat_service.add_message(
        conversation_id=request.conversation_id,
        user_id=user_id,
        role="assistant",
        content=result["answer"],
    )

    return ChatResponse(
        answer=result["answer"],
        retrieved_chunks=result["retrieved_chunks"],
        memories=result["memories"],
        episodes=result["episodes"],
        procedures=result["procedures"],
        graph_facts=result["graph_facts"],
    )
