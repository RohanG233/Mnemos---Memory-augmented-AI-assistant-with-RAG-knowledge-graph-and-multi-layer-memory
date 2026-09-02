import time
import uuid

from app.memory.maintenance import (
    find_similar_memory
)

from app.core.config import (
    MEMORY_SIMILARITY_THRESHOLD
)


PROCEDURE_PROMPT = """
Should this user message be stored as
procedural memory?

Store only if it is a long-term instruction
for how the assistant should behave.

Reply ONLY:

Yes

or

No

User:
{user_input}
"""


class ProceduralMemoryService:

    def __init__(
        self,
        collection,
        embedding_model,
        llm_service
    ):

        self.collection = collection
        self.embedding_model = embedding_model
        self.llm_service = llm_service


    def process(
        self,
        user_input,
        user_id: str,
    ):

        prompt = (
            PROCEDURE_PROMPT.format(
                user_input=user_input
            )
        )

        decision = (
            self.llm_service
            .generate(
                [
                    {
                        "role": "system",
                        "content": prompt
                    }
                ]
            )
            .strip()
            .lower()
        )

        if decision != "yes":
            return None

        similar_procedure = (
            find_similar_memory(
                self.collection,
                self.embedding_model,
                user_input,
                user_id=user_id,
                threshold=(
                    MEMORY_SIMILARITY_THRESHOLD
                )
            )
        )

        if similar_procedure:

            return {
                "stored": False,
                "duplicate": True,
                "procedure":
                    similar_procedure[
                        "document"
                    ]
            }

        procedure_id = str(
            uuid.uuid4()
        )

        now = time.time()

        self.collection.add(
            ids=[procedure_id],

            documents=[
                user_input
            ],

            metadatas=[
            {
                "user_id": user_id,

                "source":
                    "user_instruction",

                "created_at":
                    now,

                "last_accessed":
                    now,

                "access_count":
                    0,

                "importance":
                    1.0
            }
        ]
        )

        return {
            "stored": True,
            "duplicate": False,
            "id": procedure_id
        }