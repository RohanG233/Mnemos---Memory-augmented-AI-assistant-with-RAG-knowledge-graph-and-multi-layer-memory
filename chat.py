import requests
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter
import math
import time
import uuid

chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load Text File
with open("spider.txt", "r", encoding="utf-8") as file:
    text = file.read()


N = 6
messages = []
conversation_summary = ""
collection = chroma_client.get_or_create_collection(name="documents", embedding_function=embedding_function)
memory_collection = chroma_client.get_or_create_collection(
    name="memory",
    embedding_function=embedding_function
)

episode_collection = chroma_client.get_or_create_collection(
    name="episodes",
    embedding_function=embedding_function
)

procedure_collection = chroma_client.get_or_create_collection(
    name="procedures",
    embedding_function=embedding_function
)

# Chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=70)
chunks = splitter.split_text(text)

import bm25s
import Stemmer

stemmer = Stemmer.Stemmer("english")

corpus_tokens = bm25s.tokenize(
    chunks,
    stopwords="en",
    stemmer=stemmer
)

bm25 = bm25s.BM25()
bm25.index(corpus_tokens)

# Store it in Chroma DB
if collection.count() == 0:
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[
            {
                "source": "spider.txt",
                "chunk": i
            }
            for i in range(len(chunks))
        ]
    )

persona = {
  "role": "system",
  "content": "You are a helpful, knowledgeable, and reliable AI assistant. Maintain context across the conversation and answer the user's most recent message while considering relevant previous messages. Be accurate, concise, and clear. If you are uncertain, state your uncertainty instead of inventing information. Ask clarifying questions only when necessary. Format responses for readability using paragraphs, bullet points, or code blocks when appropriate. Be polite and professional."
}

messages.append(persona)

from collections import defaultdict

def reciprocal_rank_fusion(rankings, k=60):
    scores = defaultdict(float)

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1 / (k + rank)

    return sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

def maintain_memories(collection):
    now = time.time()

    results = collection.get(
        include=["metadatas"]
    )

    ids = results["ids"]
    metadatas = results["metadatas"]

    for memory_id, metadata in zip(ids, metadatas):

        importance = metadata.get("importance", 0.5)
        last_accessed = metadata.get("last_accessed", now)
        access_count = metadata.get("access_count", 0)

        age_days = (now - last_accessed) / 86400

        # Recency decay
        recency = math.exp(-0.05 * age_days)

        # Usage reinforcement
        usage = min(1.0, math.log1p(access_count) / 5)

        # Final memory strength
        score = (
            0.5 * importance +
            0.3 * recency +
            0.2 * usage
        )

        if score < 0.15:

            print(
                f"FORGOTTEN: {memory_id} | "
                f"score={score:.3f}"
            )

            collection.delete(
                ids=[memory_id]
            )

        else:

            collection.update(
                ids=[memory_id],
                metadatas=[
                    {
                        **metadata,
                        "memory_score": score
                    }
                ]
            )

def reinforce_memories(collection, query_embedding, n_results=3):

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=min(n_results, collection.count())
    )

    retrieved_documents = results["documents"][0]
    memory_ids = results["ids"][0]

    now = time.time()

    for memory_id in memory_ids:

        memory_data = collection.get(
            ids=[memory_id],
            include=["metadatas"]
        )

        metadata = memory_data["metadatas"][0]

        access_count = metadata.get("access_count", 0)

        collection.update(
            ids=[memory_id],
            metadatas=[
                {
                    **metadata,
                    "access_count": access_count + 1,
                    "last_accessed": now
                }
            ]
        )

    return retrieved_documents

def find_similar_memory(collection, text, threshold=0.20):

    if collection.count() == 0:
        return None

    embedding = model.encode(text)

    results = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=1,
        include=["documents", "metadatas", "distances"]
    )

    if not results["ids"][0]:
        return None

    distance = results["distances"][0][0]

    if distance <= threshold:
        return {
            "id": results["ids"][0][0],
            "document": results["documents"][0][0],
            "metadata": results["metadatas"][0],
            "distance": distance
        }

    return None

conversation_count = 0

while True:
    user_input = input("You : ").strip()
    conversation_count += 1
    messages.append({"role": "user", "content": user_input})

    query = user_input

#----------------- Retrieval Phase -----------------------
    # Generate embedding for memory search
    query_embedding = model.encode(query)


        # ---------------- Semantic Memory ----------------

    retrieved_memories = []

    if memory_collection.count() > 0:
        retrieved_memories = reinforce_memories(
            memory_collection,
            query_embedding,
            n_results=3
        )

    # ---------------- Episodic Memory ----------------

    retrieved_episodes = []

    if episode_collection.count() > 0:

        retrieved_episodes = reinforce_memories(
                episode_collection,
                query_embedding,
                n_results=3
            )


    # ---------------- Procedural Memory ----------------

    retrieved_procedures = []

    if procedure_collection.count() > 0:
        
        retrieved_procedures = reinforce_memories(
            procedure_collection,
            query_embedding,
            n_results=3
        )

    query_tokens = bm25s.tokenize(
        query,
        stemmer=stemmer
    )

    bm25_results, bm25_scores = bm25.retrieve(
        query_tokens,
        k=5
    )

    bm25_doc_ids = bm25_results[0].tolist()

    # Vector HNSW Retrieval
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=5
    )

    vector_doc_ids = [
        int(id.split("_")[1])
        for id in results["ids"][0]
    ]

    rrf_results = reciprocal_rank_fusion(
        [
            bm25_doc_ids,
            vector_doc_ids
        ]
    )

    TOP_K = 5

    # Chunks based on RRF
    retrieved_chunks = []

    for doc_id, score in rrf_results[:TOP_K]:
        retrieved_chunks.append(chunks[doc_id])

# --------------- Context Building ---------------------
    context = ""
    for i, chunk in enumerate(retrieved_chunks, start=1):
        context += f"[Document {i}]\n{chunk}\n\n"

    memory_context = ""
    for i, memory in enumerate(retrieved_memories, start=1):
        memory_context += f"[Memory {i}]\n{memory}\n\n"

    episode_context = ""
    for i, episode in enumerate(retrieved_episodes, start=1):
        episode_context += f"[Episode {i}]\n{episode}\n\n"

    procedure_context = ""
    for i, procedure in enumerate(retrieved_procedures, start=1):
        procedure_context += f"[Procedure {i}]\n{procedure}\n\n"

    # system_prompt = f"""
    # You are a helpful, knowledgeable, and reliable AI assistant.

    # Answer the user's question using the retrieved documents below.

    # Rules:
    # - Use the documents whenever they contain the answer.
    # - If the documents do not contain enough information, say you don't know.
    # - Do not invent facts.
    # - If useful, combine information from multiple documents.

    # Retrieved Documents:

    # {context}
    # """

# ----------- Response Generation ---------------
    system_prompt = f"""
    You are a helpful, knowledgeable, and reliable AI assistant.

    Use the following sources in order:

    1. Conversation Summary : {conversation_summary}
    2. Procedural Memory : {procedure_context}
    3. Relevant Episodes : {episode_context}
    4. Relevant Semantic Memories : {memory_context}
    5. Retrieved Documents : {context}

    Rules:
    - Use conversation memories when the user asks about previous conversations, personal preferences, or past decisions.
    - Use the retrieved documents when answering questions about the knowledge base.
    - If neither the memories nor the retrieved documents contain the answer, respond:
    "I don't know based on the available context."
    - Do not invent facts.
    """

    prompt_messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Add conversation history (skip the old system prompt)
    prompt_messages.extend(messages[1:])

    # print("\nRetrieved Documents:\n")

    # for i, chunk in enumerate(retrieved_chunks, start=1):
    #     print(f"Document {i}")
    #     print(chunk)
    #     print("-" * 50)
    
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest",
        "messages": prompt_messages,
        "stream": False
    }


    response = requests.post(url, json=payload)
    data = response.json()
    assistant_reply = data["message"]["content"]
    print("Assistant : ", assistant_reply)
    messages.append({"role":"assistant", "content":assistant_reply})

# ---------------Short Term Memory Management ---------------
    if len(messages) > 1 + N * 2:
        old_messages = messages[1:-N]
        summary_messages = [
            {
                "role": "system",
                "content":
                    f"""
                    Current Summary:
                    {conversation_summary}

                    Update the summary using the new conversation.
                    Keep it under 8 sentences.
                    Preserve important user facts, goals, preferences and decisions.
                    """
            }
        ]

        summary_messages.extend(old_messages)
        summary_payload = {
            "model": "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest",
            "messages": summary_messages,
            "stream": False
        }

        summary_response = requests.post(
            url,
            json=summary_payload
        )
        conversation_summary = summary_response.json()["message"]["content"]
        del messages[1:-N]


# -----------------Long Term Memory Management -------------
# Semantic Memory
    semantic_prompt = f"""
    Analyze the following user message.

    Decide whether it should be stored as long-term semantic memory.

    Store only if it contains:
    - personal facts
    - preferences
    - long-term goals
    - stable information

    If it should be stored, also assign an importance score from 0.0 to 1.0.

    Reply ONLY in this format:

    STORE: Yes
    IMPORTANCE: 0.0

    or

    STORE: No

    User:
    {user_input}
    """

    semantic_payload = {
        "model": "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest",
        "messages": [
            {
                "role": "system",
                "content": semantic_prompt
            }
        ],
        "stream": False
    }

    semantic_response = requests.post(
        url,
        json=semantic_payload
    )

    semantic_result = semantic_response.json()["message"]["content"].strip()

    should_store = "STORE: Yes" in semantic_result

    importance = 0.5

    if should_store:
        for line in semantic_result.splitlines():
            if line.startswith("IMPORTANCE:"):
                try:
                    importance = float(line.split(":")[1].strip())
                    importance = max(0.0, min(1.0, importance))
                except ValueError:
                    importance = 0.5

    if should_store:
        similar_memory = find_similar_memory(
            memory_collection,
            user_input
        )

        if similar_memory:

            print("Duplicate/similar memory detected:")
            print(similar_memory["document"])

        else:
            memory_id = str(uuid.uuid4())
            now = time.time()

            memory_collection.add(
                ids=[memory_id],
                documents=[user_input],
                metadatas=[
                    {
                        "source": "conversation",
                        "created_at": now,
                        "last_accessed": now,
                        "access_count": 0,
                        "importance": importance
                    }
                ]
            )

# Episodic Memory
    episode_check_prompt = f"""
    Decide whether this interaction is important enough to store
    as episodic memory.

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
    - Requests to remember a fact (those belong to semantic memory).
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

    episode_check_payload = {
        "model": "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest",
        "messages": [
            {
                "role": "system",
                "content": episode_check_prompt
            }
        ],
        "stream": False
    }

    episode_check = requests.post(
        url,
        json=episode_check_payload
    )

    store_episode = (
        episode_check.json()["message"]["content"]
        .strip()
        .lower() == "yes"
    )

    if store_episode:
        episode_prompt = f"""
        Create a concise episodic memory from this interaction.

        Rules:
        - Describe the event from a neutral third-person perspective.
        - Do NOT use "I", "me", "my", "we", or "assistant".
        - Do NOT invent information.
        - Do NOT include unnecessary conversational details.
        - Focus on what happened, what was learned, and what decision was made.
        - Maximum 3 sentences.

        Return ONLY the episodic memory.

        User:
        {user_input}

        Assistant:
        {assistant_reply}
        """

        episode_payload = {
            "model": "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest",
            "messages": [
                {
                    "role": "system",
                    "content": episode_prompt
                }
            ],
            "stream": False
        }

        episode_response = requests.post(
            url,
            json=episode_payload
        )

        episode_summary = episode_response.json()["message"]["content"]
        similar_episode = find_similar_memory(
            episode_collection,
            episode_summary
        )

        if similar_episode:

            print("\nDuplicate episode detected:")
            print(similar_episode["document"])
            print("Distance:", similar_episode["distance"])

        else:
            episode_id = str(uuid.uuid4())
            now = time.time()

            episode_collection.add(
                ids=[episode_id],
                documents=[episode_summary],
                metadatas=[
                    {
                        "source": "conversation",
                        "created_at": now,
                        "last_accessed": now,
                        "access_count": 0,
                        "importance": 0.7
                    }
                ]
            )

# Procedural Memory
    procedure_prompt = f"""
    Should this user message be stored as procedural memory?

    Store only if it is a long-term instruction for how the assistant should behave.

    Reply ONLY:

    Yes or No

    User:
    {user_input}
    """

    procedure_payload = {
        "model": "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest",
        "messages": [
            {
                "role": "system",
                "content": procedure_prompt
            }
        ],
        "stream": False
    }

    procedure_response = requests.post(
        url,
        json=procedure_payload
    )

    should_store_procedure = (
        procedure_response.json()["message"]["content"]
        .strip()
        .lower() == "yes"
    )

    if should_store_procedure:
        similar_procedure = find_similar_memory(
            procedure_collection,
            user_input
        )

        if similar_procedure:
            print("\nDuplicate procedure detected:")
            print(similar_procedure["document"])
            print("Distance:", similar_procedure["distance"])
        else:
            procedure_id = str(uuid.uuid4())
            now = time.time()

            procedure_collection.add(
                ids=[procedure_id],
                documents=[user_input],
                metadatas=[
                    {
                        "source": "user_instruction",
                        "created_at": now,
                        "last_accessed": now,
                        "access_count": 0,
                        "importance": 1.0
                    }
                ]
            )

    if conversation_count % 10 == 0:
        maintain_memories(memory_collection)
        maintain_memories(episode_collection)