import logging
import time
import uuid

from app.memory.maintenance import find_similar_memory
from app.core.config import MEMORY_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)


SEMANTIC_PROMPT = """
Analyze the following user message.

Decide whether it should be stored as long-term semantic memory.

Store only if it contains:
- personal facts
- preferences
- long-term goals
- stable information

If it should be stored, also assign an importance score from 0.0 to 1.0.

Reply ONLY in this exact format:

STORE: Yes
IMPORTANCE: 0.8

or

STORE: No

User:
{user_input}
"""


class SemanticMemoryService:

    def __init__(self, collection, embedding_model, llm_service):
        self.collection = collection
        self.embedding_model = embedding_model
        self.llm_service = llm_service


    def process(self, user_input: str, user_id: str):

        prompt = SEMANTIC_PROMPT.format(user_input=user_input)

        result = self.llm_service.generate(
            [{"role": "system", "content": prompt}]
        ).strip()

        logger.info("Semantic classifier raw response: %r", result)

        should_store = "STORE: Yes" in result

        importance = 0.5

        if should_store:
            for line in result.splitlines():
                if line.startswith("IMPORTANCE:"):
                    try:
                        importance = float(line.split(":")[1].strip())
                        importance = max(0.0, min(1.0, importance))
                    except ValueError:
                        importance = 0.5

        if not should_store:
            logger.info("Semantic: not storing (STORE: Yes not found)")
            return None

        logger.info("Semantic: storing for user=%s importance=%.2f", user_id, importance)

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
                "memory": similar["document"],
            }

        memory_id = str(uuid.uuid4())
        now = time.time()

        self.collection.add(
            ids=[memory_id],
            documents=[user_input],
            metadatas=[{
                "user_id": user_id,
                "source": "conversation",
                "created_at": now,
                "last_accessed": now,
                "access_count": 0,
                "importance": importance,
            }],
        )

        return {
            "stored": True,
            "duplicate": False,
            "id": memory_id,
            "importance": importance,
        }
