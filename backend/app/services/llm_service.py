import json
import logging

import requests

from app.core.config import (
    OLLAMA_URL,
    LLM_MODEL,
    LLM_TIMEOUT,
)

logger = logging.getLogger(__name__)


# --------------------------------
# Custom exceptions
# --------------------------------

class LLMUnavailableError(Exception):
    """Raised when Ollama is unreachable."""


class LLMModelNotFoundError(Exception):
    """Raised when the requested model does not exist."""


class LLMResponseError(Exception):
    """Raised when the Ollama response is malformed."""


# --------------------------------
# LLM Service
# --------------------------------

class LLMService:

    def __init__(
        self,
        url: str = OLLAMA_URL,
        model: str = LLM_MODEL,
        timeout: int = LLM_TIMEOUT,
    ):
        self.url = url
        self.model = model
        self.timeout = timeout

        logger.info(
            "LLMService initialised — url=%s model=%s timeout=%ss",
            self.url,
            self.model,
            self.timeout,
        )


    def generate(
        self,
        messages: list[dict],
        json_format: bool = False,
    ) -> str:
        """
        Send a chat completion request to Ollama.

        Parameters
        ----------
        messages : list[dict]
            List of {role, content} dicts.
        json_format : bool
            When True, ask Ollama to return JSON.

        Returns
        -------
        str
            The assistant's reply text.

        Raises
        ------
        LLMUnavailableError
            When Ollama cannot be reached.
        LLMModelNotFoundError
            When the model is not available.
        LLMResponseError
            When the response is malformed.
        """

        payload: dict = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        if json_format:
            payload["format"] = "json"

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout,
            )
        except requests.exceptions.ConnectionError as exc:
            raise LLMUnavailableError(
                f"Cannot connect to Ollama at {self.url}. "
                "Make sure Ollama is running."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise LLMUnavailableError(
                f"Ollama request timed out after {self.timeout}s."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise LLMUnavailableError(
                f"Unexpected error communicating with Ollama: {exc}"
            ) from exc

        # 404 from Ollama typically means model not found
        if response.status_code == 404:
            raise LLMModelNotFoundError(
                f"Model '{self.model}' was not found in Ollama. "
                "Run: ollama pull <model-name>"
            )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise LLMResponseError(
                f"Ollama returned HTTP {response.status_code}: "
                f"{response.text[:200]}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMResponseError(
                f"Ollama returned non-JSON response: {response.text[:200]}"
            ) from exc

        try:
            content: str = data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise LLMResponseError(
                f"Unexpected Ollama response structure: {data}"
            ) from exc

        # Validate JSON when caller requested it
        if json_format:
            try:
                json.loads(content)
            except json.JSONDecodeError:
                logger.warning(
                    "LLM returned non-JSON despite json_format=True: %s",
                    content[:200],
                )
                # Return the raw string so callers can decide what to do
                # (extraction code already handles json.JSONDecodeError)

        return content


    def is_available(self) -> bool:
        """
        Quick connectivity check — does NOT generate text.
        Returns True if Ollama responds, False otherwise.
        """
        base = self.url.split("/api")[0]
        try:
            r = requests.get(
                f"{base}/api/tags",
                timeout=5,
            )
            return r.ok
        except Exception:
            return False
