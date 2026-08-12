import numpy as np

from app.core.database import (
    model,
    document_collection,
    memory_collection,
    episode_collection,
    procedure_collection
)

from app.core.config import (
    FINAL_TOP_K,
    MEMORY_RETRIEVAL_TOP_K
)

from app.retrieval.vector import (
    VectorRetriever
)

from app.retrieval.fusion import (
    reciprocal_rank_fusion
)

from app.graph.retrieval import (
    graph_context
)

from app.graph.extraction import (
    TripleExtractor
)

from app.graph.store import (
    add_triple,
    save_graph
)

from app.memory.maintenance import (
    reinforce_memories
)

from app.memory.short_term import (
    ConversationMemory
)

from app.memory.semantic import (
    SemanticMemoryService
)

from app.memory.episodic import (
    EpisodicMemoryService
)

from app.memory.procedural import (
    ProceduralMemoryService
)


class RAGService:

    def __init__(
        self,
        graph,
        document_service,
        llm_service
    ):

        self.graph = graph

        self.document_service = document_service

        self.llm = llm_service

        self.vector_retriever = (
            VectorRetriever(
                document_collection
            )
        )

        self.triple_extractor = (
            TripleExtractor(
                llm_service
            )
        )

        self.conversation = (
            ConversationMemory()
        )

        self.semantic_memory = (
            SemanticMemoryService(
                memory_collection,
                model,
                llm_service
            )
        )

        self.episodic_memory = (
            EpisodicMemoryService(
                episode_collection,
                model,
                llm_service
            )
        )

        self.procedural_memory = (
            ProceduralMemoryService(
                procedure_collection,
                model,
                llm_service
            )
        )


    def retrieve(
        self,
        query,
        *args,
        **kwargs
    ):

        bm25 = self.document_service.get_bm25()

        if bm25 is None:
            bm25_doc_ids = []
            bm25_scores = []
        else:
            bm25_doc_ids, bm25_scores = bm25.search(query)

        # -------------------------
        # Query embedding
        # -------------------------

        query_embedding = model.encode(
            query
        )


        # -------------------------
        # Semantic Memory
        # -------------------------

        retrieved_memories = []

        if memory_collection.count() > 0:

            retrieved_memories = (
                reinforce_memories(
                    memory_collection,
                    query_embedding,
                    n_results=(
                        MEMORY_RETRIEVAL_TOP_K
                    )
                )
            )


        # -------------------------
        # Episodic Memory
        # -------------------------

        retrieved_episodes = []

        if episode_collection.count() > 0:

            retrieved_episodes = (
                reinforce_memories(
                    episode_collection,
                    query_embedding,
                    n_results=(
                        MEMORY_RETRIEVAL_TOP_K
                    )
                )
            )


        # -------------------------
        # Procedural Memory
        # -------------------------

        retrieved_procedures = []

        if procedure_collection.count() > 0:

            retrieved_procedures = (
                reinforce_memories(
                    procedure_collection,
                    query_embedding,
                    n_results=(
                        MEMORY_RETRIEVAL_TOP_K
                    )
                )
            )




        # -------------------------
        # Vector Search
        # -------------------------

        vector_doc_ids = (
            self.vector_retriever.search(
                query_embedding
            )
        )


        # -------------------------
        # Reciprocal Rank Fusion
        # -------------------------

        rrf_results = (
            reciprocal_rank_fusion(
                [
                    bm25_doc_ids,
                    vector_doc_ids
                ]
            )
        )


        # -------------------------
        # Graph Retrieval
        # -------------------------

        graph_facts = graph_context(
            self.graph,
            query,
            hops=2
        )


        # -------------------------
        # Final Chunks
        # -------------------------

        retrieved_chunks = []

        if bm25 is not None:
            for (
                doc_id,
                score
            ) in rrf_results[:FINAL_TOP_K]:

                retrieved_chunks.append(
                    bm25.documents[
                        doc_id
                    ]
                )


        return {
            "query_embedding":
                query_embedding,

            "memories":
                retrieved_memories,

            "episodes":
                retrieved_episodes,

            "procedures":
                retrieved_procedures,

            "chunks":
                retrieved_chunks,

            "graph_facts":
                graph_facts,

            "bm25_scores":
                bm25_scores,

            "rrf_results":
                rrf_results
        }


    def build_context(
        self,
        retrieved
    ):

        context = ""

        for i, chunk in enumerate(
            retrieved["chunks"],
            start=1
        ):

            context += (
                f"[Document {i}]\n"
                f"{chunk}\n\n"
            )


        memory_context = ""

        for i, memory in enumerate(
            retrieved["memories"],
            start=1
        ):

            memory_context += (
                f"[Memory {i}]\n"
                f"{memory}\n\n"
            )


        episode_context = ""

        for i, episode in enumerate(
            retrieved["episodes"],
            start=1
        ):

            episode_context += (
                f"[Episode {i}]\n"
                f"{episode}\n\n"
            )


        procedure_context = ""

        for i, procedure in enumerate(
            retrieved["procedures"],
            start=1
        ):

            procedure_context += (
                f"[Procedure {i}]\n"
                f"{procedure}\n\n"
            )


        graph_fact_context = ""

        for i, fact in enumerate(
            retrieved["graph_facts"],
            start=1
        ):

            graph_fact_context += (
                f"[Graph Fact {i}]\n"
                f"{fact}\n\n"
            )


        return {
            "documents":
                context,

            "memories":
                memory_context,

            "episodes":
                episode_context,

            "procedures":
                procedure_context,

            "graph":
                graph_fact_context
        }


    def generate_response(
        self,
        user_input,
        retrieved,
        contexts
    ):

        system_prompt = f"""
You are a helpful, knowledgeable,
and reliable AI assistant.

Use the following sources in order:

1. Conversation Summary:
{self.conversation.get_summary()}

2. Procedural Memory:
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

- Use conversation memories when the user asks
  about previous conversations, personal
  preferences, or past decisions.

- Use the retrieved documents when answering
  questions about the knowledge base.

- If neither the memories nor the retrieved
  documents contain the answer, respond:

"I don't know based on the available context."

- Do not invent facts.
"""


        prompt_messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]


        prompt_messages.extend(
            self.conversation
            .get_messages()
        )


        response = self.llm.generate(
            prompt_messages
        )

        return response


    def update_graph(
        self,
        user_input
    ):

        triples = (
            self.triple_extractor
            .extract_triples_from_text(
                user_input
            )
        )

        for triple in triples:

            subject = triple.get(
                "subject"
            )

            relation = triple.get(
                "relation"
            )

            obj = triple.get(
                "object"
            )

            if (
                subject
                and relation
                and obj
            ):

                add_triple(
                    self.graph,
                    subject,
                    relation,
                    obj
                )

        save_graph(
            self.graph
        )


    def update_memories(
        self,
        user_input,
        assistant_reply
    ):

        semantic_result = (
            self.semantic_memory.process(
                user_input
            )
        )

        episodic_result = (
            self.episodic_memory.process(
                user_input,
                assistant_reply
            )
        )

        procedural_result = (
            self.procedural_memory.process(
                user_input
            )
        )

        return {
            "semantic":
                semantic_result,

            "episodic":
                episodic_result,

            "procedural":
                procedural_result
        }


    def chat(
        self,
        user_input
    ):

        # -------------------------
        # Add user message
        # -------------------------

        self.conversation.add_message(
            "user",
            user_input
        )


        # -------------------------
        # Retrieval
        # -------------------------

        retrieved = self.retrieve(
            user_input
        )


        # -------------------------
        # Context
        # -------------------------

        contexts = self.build_context(
            retrieved
        )


        # -------------------------
        # Generate
        # -------------------------

        assistant_reply = (
            self.generate_response(
                user_input,
                retrieved,
                contexts
            )
        )


        # -------------------------
        # Add assistant message
        # -------------------------

        self.conversation.add_message(
            "assistant",
            assistant_reply
        )


        # -------------------------
        # Graph Update
        # -------------------------

        self.update_graph(
            user_input
        )


        # -------------------------
        # Memory Update
        # -------------------------

        memory_results = (
            self.update_memories(
                user_input,
                assistant_reply
            )
        )


        return {
            "answer":
                assistant_reply,

            "retrieved_chunks":
                retrieved["chunks"],

            "memories":
                retrieved["memories"],

            "episodes":
                retrieved["episodes"],

            "procedures":
                retrieved["procedures"],

            "graph_facts":
                retrieved["graph_facts"],

            "memory_updates":
                memory_results
        }