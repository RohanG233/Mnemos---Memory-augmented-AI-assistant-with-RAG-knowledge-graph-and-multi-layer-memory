import logging

from app.core.database import (
    model,
    document_collection,
    memory_collection,
    episode_collection,
    procedure_collection,
)

from app.core.config import (
    FINAL_TOP_K,
    MEMORY_RETRIEVAL_TOP_K,
)

from app.retrieval.vector import VectorRetriever
from app.retrieval.fusion import reciprocal_rank_fusion
from app.graph.retrieval import graph_context
from app.graph.extraction import TripleExtractor
from app.graph.store import add_triple, save_graph, load_graph
from app.memory.maintenance import reinforce_memories
from app.memory.short_term import ConversationMemory
from app.memory.semantic import SemanticMemoryService
from app.memory.episodic import EpisodicMemoryService
from app.memory.procedural import ProceduralMemoryService
from app.services.llm_service import LLMUnavailableError, LLMResponseError

logger = logging.getLogger(__name__)


def _has_user_documents(collection, user_id: str) -> bool:
    """Return True if the collection contains at least one entry for user."""
    try:
        result = collection.get(where={"user_id": user_id}, include=[], limit=1)
        return len(result["ids"]) > 0
    except Exception:
        return False


class RAGService:

    def __init__(self, document_service, llm_service):
        self.document_service = document_service
        self.llm = llm_service

        self.vector_retriever = VectorRetriever(document_collection)

        self.triple_extractor = TripleExtractor(llm_service)

        # Per-user in-process short-term memory.
        # NOTE: This is lost on restart — acceptable for a stateless
        # deployment where MongoDB holds durable conversation history.
        self.user_conversations: dict[str, ConversationMemory] = {}

        self.semantic_memory = SemanticMemoryService(
            memory_collection, model, llm_service
        )
        self.episodic_memory = EpisodicMemoryService(
            episode_collection, model, llm_service
        )
        self.procedural_memory = ProceduralMemoryService(
            procedure_collection, model, llm_service
        )


    # -------------------------
    # Short-term conversation
    # -------------------------

    def get_conversation(self, user_id: str) -> ConversationMemory:
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = ConversationMemory()
        return self.user_conversations[user_id]


    # -------------------------
    # Retrieval
    # -------------------------

    def retrieve(self, query: str, user_id: str) -> dict:

        # --- BM25 ---
        bm25 = self.document_service.get_bm25(user_id)

        if bm25 is None or not bm25.documents:
            bm25_doc_ids: list[int] = []
            bm25_scores: list[float] = []
        else:
            bm25_doc_ids, bm25_scores = bm25.search(query)

        # --- Query embedding ---
        query_embedding = model.encode(query)

        # --- Memory retrieval (only when user has data) ---
        retrieved_memories: list[str] = []
        if _has_user_documents(memory_collection, user_id):
            try:
                retrieved_memories = reinforce_memories(
                    memory_collection,
                    query_embedding,
                    user_id=user_id,
                    n_results=MEMORY_RETRIEVAL_TOP_K,
                )
            except Exception:
                logger.exception("Semantic memory retrieval failed for user=%s", user_id)

        retrieved_episodes: list[str] = []
        if _has_user_documents(episode_collection, user_id):
            try:
                retrieved_episodes = reinforce_memories(
                    episode_collection,
                    query_embedding,
                    user_id=user_id,
                    n_results=MEMORY_RETRIEVAL_TOP_K,
                )
            except Exception:
                logger.exception("Episodic memory retrieval failed for user=%s", user_id)

        retrieved_procedures: list[str] = []
        if _has_user_documents(procedure_collection, user_id):
            try:
                retrieved_procedures = reinforce_memories(
                    procedure_collection,
                    query_embedding,
                    user_id=user_id,
                    n_results=MEMORY_RETRIEVAL_TOP_K,
                )
            except Exception:
                logger.exception("Procedural memory retrieval failed for user=%s", user_id)

        # --- Vector search (returns Chroma string IDs) ---
        vector_chroma_ids: list[str] = self.vector_retriever.search(
            query_embedding, user_id=user_id
        )

        # --- RRF over BM25 integer indices only ---
        # BM25 returns integer indices into bm25.documents.
        # Vector returns Chroma string IDs which cannot be merged
        # with BM25 integer indices via RRF.
        # We fuse separately: BM25 gives text directly; vector gives
        # Chroma IDs we resolve to text.
        # Simple approach: collect unique chunks from both, deduplicate.
        retrieved_chunks: list[str] = []

        # From BM25
        if bm25 is not None:
            for idx in bm25_doc_ids[:FINAL_TOP_K]:
                if 0 <= idx < len(bm25.documents):
                    chunk = bm25.documents[idx]
                    if chunk not in retrieved_chunks:
                        retrieved_chunks.append(chunk)

        # From vector (fetch text from Chroma)
        if vector_chroma_ids:
            try:
                chroma_result = document_collection.get(
                    ids=vector_chroma_ids,
                    include=["documents"],
                )
                for chunk in (chroma_result.get("documents") or []):
                    if chunk and chunk not in retrieved_chunks:
                        retrieved_chunks.append(chunk)
            except Exception:
                logger.exception("Failed to fetch vector result texts from Chroma")

        retrieved_chunks = retrieved_chunks[:FINAL_TOP_K]

        # --- Graph retrieval ---
        graph_facts: list[str] = []
        try:
            graph = load_graph(user_id)
            graph_facts = graph_context(graph, query, hops=2)
        except Exception:
            logger.exception("Graph retrieval failed for user=%s", user_id)

        return {
            "query_embedding": query_embedding,
            "memories": retrieved_memories,
            "episodes": retrieved_episodes,
            "procedures": retrieved_procedures,
            "chunks": retrieved_chunks,
            "graph_facts": graph_facts,
            "bm25_scores": bm25_scores,
        }


    # -------------------------
    # Context building
    # -------------------------

    def build_context(self, retrieved: dict) -> dict:

        context = ""
        for i, chunk in enumerate(retrieved["chunks"], start=1):
            context += f"[Document {i}]\n{chunk}\n\n"

        memory_context = ""
        for i, memory in enumerate(retrieved["memories"], start=1):
            memory_context += f"[Memory {i}]\n{memory}\n\n"

        episode_context = ""
        for i, episode in enumerate(retrieved["episodes"], start=1):
            episode_context += f"[Episode {i}]\n{episode}\n\n"

        procedure_context = ""
        for i, procedure in enumerate(retrieved["procedures"], start=1):
            procedure_context += f"[Procedure {i}]\n{procedure}\n\n"

        graph_fact_context = ""
        for i, fact in enumerate(retrieved["graph_facts"], start=1):
            graph_fact_context += f"[Graph Fact {i}]\n{fact}\n\n"

        return {
            "documents": context,
            "memories": memory_context,
            "episodes": episode_context,
            "procedures": procedure_context,
            "graph": graph_fact_context,
        }


    # -------------------------
    # Response generation
    # -------------------------

    def generate_response(
        self,
        user_input: str,
        retrieved: dict,
        contexts: dict,
        user_id: str,
    ) -> str:

        conversation = self.get_conversation(user_id)

        system_prompt = f"""You are a helpful, knowledgeable, and reliable AI assistant.

Use the following sources in order of priority:

1. Conversation Summary:
{conversation.get_summary()}

2. Procedural Memory (how the assistant should behave):
{contexts["procedures"]}

3. Relevant Episodes:
{contexts["episodes"]}

4. Relevant Semantic Memories:
{contexts["memories"]}

5. Retrieved Documents:
{contexts["documents"]}

6. Knowledge Graph:
{contexts["graph"]}

Rules:
- Use conversation memories when the user asks about previous conversations, personal preferences, or past decisions.
- Use retrieved documents when answering questions about the knowledge base.
- If neither memories nor documents contain the answer, say: "I don't know based on the available context."
- Do not invent facts.
"""

        prompt_messages = [
            {"role": "system", "content": system_prompt}
        ]
        prompt_messages.extend(conversation.get_messages())
        prompt_messages.append({"role": "user", "content": user_input})

        response = self.llm.generate(prompt_messages)
        return response


    # -------------------------
    # Graph update
    # -------------------------

    def update_graph(self, user_input: str, user_id: str) -> None:
        try:
            graph = load_graph(user_id)
            triples = self.triple_extractor.extract_triples_from_text(user_input)

            for triple in triples:
                subject = triple.get("subject")
                relation = triple.get("relation")
                obj = triple.get("object")

                if subject and relation and obj:
                    add_triple(graph, subject, relation, obj)

            save_graph(graph, user_id)
        except Exception:
            logger.exception(
                "Graph update failed for user=%s — continuing without graph update.",
                user_id,
            )


    # -------------------------
    # Memory update
    # -------------------------

    def update_memories(
        self,
        user_input: str,
        assistant_reply: str,
        user_id: str,
    ) -> dict:
        results: dict = {}

        try:
            results["semantic"] = self.semantic_memory.process(
                user_input, user_id=user_id
            )
        except Exception:
            logger.exception("Semantic memory update failed for user=%s", user_id)
            results["semantic"] = None

        try:
            results["episodic"] = self.episodic_memory.process(
                user_input, assistant_reply, user_id=user_id
            )
        except Exception:
            logger.exception("Episodic memory update failed for user=%s", user_id)
            results["episodic"] = None

        try:
            results["procedural"] = self.procedural_memory.process(
                user_input, user_id=user_id
            )
        except Exception:
            logger.exception("Procedural memory update failed for user=%s", user_id)
            results["procedural"] = None

        return results


    # -------------------------
    # Main chat entry point
    # -------------------------

    def chat(self, user_input: str, user_id: str) -> dict:

        conversation = self.get_conversation(user_id)
        conversation.add_message("user", user_input)

        retrieved = self.retrieve(user_input, user_id=user_id)
        contexts = self.build_context(retrieved)

        assistant_reply = self.generate_response(
            user_input, retrieved, contexts, user_id=user_id
        )

        conversation.add_message("assistant", assistant_reply)

        # Non-blocking updates (graph + memory) — failures do not abort the response
        self.update_graph(user_input, user_id=user_id)

        memory_results = self.update_memories(
            user_input, assistant_reply, user_id=user_id
        )

        return {
            "answer": assistant_reply,
            "retrieved_chunks": retrieved["chunks"],
            "memories": retrieved["memories"],
            "episodes": retrieved["episodes"],
            "procedures": retrieved["procedures"],
            "graph_facts": retrieved["graph_facts"],
            "memory_updates": memory_results,
        }
