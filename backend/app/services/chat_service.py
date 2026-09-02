from datetime import datetime, timezone
import uuid

from app.core.database import (
    conversations_collection,
    messages_collection,
)


class ChatService:

    # --------------------------------
    # Create Conversation
    # --------------------------------

    def create_conversation(
        self,
        user_id: str,
        title: str = "New Chat",
    ):

        conversation_id = str(
            uuid.uuid4()
        )

        now = datetime.now(
            timezone.utc
        )

        conversation = {
            "conversation_id":
                conversation_id,

            "user_id":
                user_id,

            "title":
                title,

            "created_at":
                now,

            "updated_at":
                now,
        }

        conversations_collection.insert_one(
            conversation
        )

        return conversation


    # --------------------------------
    # Get Conversations
    # --------------------------------

    def get_conversations(
        self,
        user_id: str,
    ):

        return list(
            conversations_collection.find(
                {
                    "user_id": user_id
                },
                {
                    "_id": 0
                }
            ).sort(
                "updated_at",
                -1
            )
        )


    # --------------------------------
    # Get Conversation Messages
    # --------------------------------

    def get_messages(
        self,
        conversation_id: str,
        user_id: str,
    ):

        conversation = (
            conversations_collection.find_one(
                {
                    "conversation_id":
                        conversation_id,

                    "user_id":
                        user_id,
                }
            )
        )

        if not conversation:
            return None

        return list(
            messages_collection.find(
                {
                    "conversation_id":
                        conversation_id,

                    "user_id":
                        user_id,
                },
                {
                    "_id": 0
                }
            ).sort(
                "created_at",
                1
            )
        )


    # --------------------------------
    # Add Message
    # --------------------------------

    def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
    ):

        conversation = (
            conversations_collection.find_one(
                {
                    "conversation_id":
                        conversation_id,

                    "user_id":
                        user_id,
                }
            )
        )

        if not conversation:
            return None

        now = datetime.now(
            timezone.utc
        )

        message = {
            "message_id":
                str(uuid.uuid4()),

            "conversation_id":
                conversation_id,

            "user_id":
                user_id,

            "role":
                role,

            "content":
                content,

            "created_at":
                now,
        }

        messages_collection.insert_one(
            message
        )

        conversations_collection.update_one(
            {
                "conversation_id":
                    conversation_id,

                "user_id":
                    user_id,
            },
            {
                "$set": {
                    "updated_at": now
                }
            }
        )

        return message


    # --------------------------------
    # Rename Conversation
    # --------------------------------

    def rename_conversation(
        self,
        conversation_id: str,
        user_id: str,
        title: str,
    ):

        result = (
            conversations_collection.update_one(
                {
                    "conversation_id":
                        conversation_id,

                    "user_id":
                        user_id,
                },
                {
                    "$set": {
                        "title":
                            title.strip(),

                        "updated_at":
                            datetime.now(
                                timezone.utc
                            ),
                    }
                }
            )
        )

        return result.modified_count > 0


    # --------------------------------
    # Delete Conversation
    # --------------------------------

    def delete_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ):

        conversation = (
            conversations_collection.find_one(
                {
                    "conversation_id":
                        conversation_id,

                    "user_id":
                        user_id,
                }
            )
        )

        if not conversation:
            return False

        messages_collection.delete_many(
            {
                "conversation_id":
                    conversation_id,

                "user_id":
                    user_id,
            }
        )

        conversations_collection.delete_one(
            {
                "conversation_id":
                    conversation_id,

                "user_id":
                    user_id,
            }
        )

        return True