"""
Procedural memory — stores behavioural instructions.

Detection strategy: keyword matching instead of LLM classification.
The 1B model is too unreliable for Yes/No classification.
We look for explicit instruction patterns in the user message.
"""

import logging
import time
import uuid

from app.memory.maintenance import find_similar_memory
from app.core.config import MEMORY_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)


# Keywords that strongly signal a behavioural instruction
_INSTRUCTION_SIGNALS = [
    "always ",
    "never ",
    "don't ",
    "do not ",
    "stop ",
    "please always",
    "please never",
    "from now on",
    "every time",
    "make sure you",
    "remember to always",
    "i want you to always",
    "i need you to always",
    "respond in",
    "reply in",
    "answer in",
    "use a",
    "be more",
    "be less",
    "start every",
    "end every",
    "format your",
    "keep your",
]


def _is_instruction(text: str) -> bool:
    """
    Returns True if the message looks like a behavioural instruction.
    Uses fast keyword matching — no LLM call needed.
    """
    lowered = text.lower()
    return any(signal in lowered for signal in _INSTRUCTION_SIGNALS)


class ProceduralMemoryService:

    def __init__(self, collection, embedding_model, llm_service):
        self.collection = collection
        self.embedding_model = embedding_model
        self.llm_service = llm_service  # kept for interface compatibility

    def process(self, user_input: str, user_id: str):

        if not _is_instruction(user_input):
            return None

        logger.info(
            "Procedural: instruction detected, storing for user=%s | %r",
            user_id,
            user_input[:80],
        )

        similar = find_similar_memory(
            self.collection,
            self.embedding_model,
            user_input,
            user_id=user_id,
            threshold=MEMORY_SIMILARITY_THRESHOLD,
        )

        if similar:
            return {
                "stored": False,
                "duplicate": True,
                "procedure": similar["document"],
            }

        procedure_id = str(uuid.uuid4())
        now = time.time()

        self.collection.add(
            ids=[procedure_id],
            documents=[user_input],
            metadatas=[{
                "user_id": user_id,
                "source": "user_instruction",
                "created_at": now,
                "last_accessed": now,
                "access_count": 0,
                "importance": 1.0,
            }],
        )

        return {
            "stored": True,
            "duplicate": False,
            "id": procedure_id,
        }
