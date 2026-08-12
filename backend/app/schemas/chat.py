from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str

    retrieved_chunks: list[str] = []

    memories: list[str] = []

    episodes: list[str] = []

    procedures: list[str] = []

    graph_facts: list[str] = []