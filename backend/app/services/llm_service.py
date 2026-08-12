import requests

from app.core.config import (
    OLLAMA_URL,
    LLM_MODEL
)


class LLMService:

    def __init__(
        self,
        url=OLLAMA_URL,
        model=LLM_MODEL
    ):
        self.url = url
        self.model = model


    def generate(
        self,
        messages,
        json_format=False
    ):
        """
        Send a chat completion request
        to the local Ollama model.
        """

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        if json_format:
            payload["format"] = "json"

        response = requests.post(
            self.url,
            json=payload
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]