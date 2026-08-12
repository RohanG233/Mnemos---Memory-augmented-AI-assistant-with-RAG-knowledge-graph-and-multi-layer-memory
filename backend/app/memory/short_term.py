from app.core.config import SHORT_TERM_MESSAGES


class ConversationMemory:

    def __init__(self):
        self.messages = []
        self.summary = ""

    def add_message(
        self,
        role,
        content
    ):
        self.messages.append(
            {
                "role": role,
                "content": content
            }
        )

    def get_messages(self):
        return self.messages

    def get_summary(self):
        return self.summary

    def set_summary(
        self,
        summary
    ):
        self.summary = summary

    def get_recent_messages(self):
        """
        Return the most recent N user/assistant
        messages.
        """

        max_messages = (
            SHORT_TERM_MESSAGES * 2
        )

        return self.messages[
            -max_messages:
        ]

    def needs_summarization(self):
        max_messages = (
            SHORT_TERM_MESSAGES * 2
        )

        return len(
            self.messages
        ) > max_messages

    def get_messages_for_summary(self):
        """
        Return older messages that should
        be summarized.
        """

        if not self.needs_summarization():
            return []

        max_messages = (
            SHORT_TERM_MESSAGES * 2
        )

        return self.messages[
            :-max_messages
        ]

    def remove_summarized_messages(self):
        """
        Keep only the most recent messages.
        """

        if not self.needs_summarization():
            return

        max_messages = (
            SHORT_TERM_MESSAGES * 2
        )

        self.messages = self.messages[
            -max_messages:
        ]


    def summarize(
        self,
        llm_service
    ):

        if not self.needs_summarization():
            return

        old_messages = (
            self.get_messages_for_summary()
        )

        formatted_messages = "\n".join(
            [
                f"{m['role']}: {m['content']}"
                for m in old_messages
            ]
        )

        prompt = f"""
    Current Summary:
    {self.summary}

    Update the summary using the new
    conversation.

    Keep it under 8 sentences.

    Preserve important user facts,
    goals, preferences and decisions.

    Conversation:
    {formatted_messages}
    """

        summary = llm_service.generate(
            [
                {
                    "role": "system",
                    "content": prompt
                }
            ]
        )

        self.summary = summary

        self.remove_summarized_messages()