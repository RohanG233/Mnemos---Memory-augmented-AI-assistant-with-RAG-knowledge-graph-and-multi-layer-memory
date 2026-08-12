import time
import uuid

from app.memory.maintenance import (
    find_similar_memory
)

from app.core.config import (
    MEMORY_SIMILARITY_THRESHOLD
)


EPISODE_CHECK_PROMPT = """
Decide whether this interaction is important
enough to store as episodic memory.

Store it ONLY if at least one is true:

- A meaningful decision was made.
- A problem was solved.
- The user learned something important.
- A project/task milestone was reached.
- A significant plan or conclusion was established.

Do NOT store:

- Simple questions and answers.
- Greetings.
- Repeated facts.
- Small conversational exchanges.
- Requests to remember a fact.
- Temporary opinions.

Reply ONLY:

Yes

or

No

User:
{user_input}

Assistant:
{assistant_reply}
"""


EPISODE_PROMPT = """
Create a concise episodic memory from this
interaction.

Rules:

- Describe the event from a neutral
  third-person perspective.
- Do NOT use "I", "me", "my", "we", or
  "assistant".
- Do NOT invent information.
- Do NOT include unnecessary conversational
  details.
- Focus on what happened, what was learned,
  and what decision was made.
- Maximum 3 sentences.

Return ONLY the episodic memory.

User:
{user_input}

Assistant:
{assistant_reply}
"""


class EpisodicMemoryService:

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
        assistant_reply
    ):

        check_prompt = (
            EPISODE_CHECK_PROMPT.format(
                user_input=user_input,
                assistant_reply=assistant_reply
            )
        )

        decision = (
            self.llm_service
            .generate(
                [
                    {
                        "role": "system",
                        "content": check_prompt
                    }
                ]
            )
            .strip()
            .lower()
        )

        if decision != "yes":
            return None

        episode_prompt = (
            EPISODE_PROMPT.format(
                user_input=user_input,
                assistant_reply=assistant_reply
            )
        )

        episode_summary = (
            self.llm_service
            .generate(
                [
                    {
                        "role": "system",
                        "content": episode_prompt
                    }
                ]
            )
            .strip()
        )

        similar_episode = (
            find_similar_memory(
                self.collection,
                self.embedding_model,
                episode_summary,
                threshold=(
                    MEMORY_SIMILARITY_THRESHOLD
                )
            )
        )

        if similar_episode:

            return {
                "stored": False,
                "duplicate": True,
                "episode":
                    similar_episode[
                        "document"
                    ]
            }

        episode_id = str(
            uuid.uuid4()
        )

        now = time.time()

        self.collection.add(
            ids=[episode_id],

            documents=[
                episode_summary
            ],

            metadatas=[
                {
                    "source":
                        "conversation",

                    "created_at":
                        now,

                    "last_accessed":
                        now,

                    "access_count":
                        0,

                    "importance":
                        0.7
                }
            ]
        )

        return {
            "stored": True,
            "duplicate": False,
            "id": episode_id,
            "episode":
                episode_summary
        }