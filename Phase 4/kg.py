"""
Hybrid Vector RAG + Knowledge Graph RAG, running entirely on local Ollama models.

Two retrieval paths feed one answer:
  - Chroma (vector search)   -> catches "sounds semantically similar"
  - NetworkX (graph search)  -> catches "is structurally/relationally connected"
"""

import re
import json
import ollama
import chromadb
import networkx as nx
from pyvis.network import Network

# Model used for the final chat answer. Small/fast is fine here since the
# model just has to read context that's already handed to it.
CHAT_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest'

# Model used for triple extraction. This is a harder task (find + structure
# facts on its own) so a bigger model noticeably improves graph quality.
# Swap back to CHAT_MODEL if you don't have the RAM for a second model.
EXTRACT_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest'

EMBED_MODEL = 'nomic-embed-text'


# ---------------------------------------------------------------------------
# Shared storage
# ---------------------------------------------------------------------------

# Persistent on-disk vector store for chunked document text.
client = chromadb.PersistentClient(path="./vector_store")
collection = client.get_or_create_collection("my_docs")

# In-memory knowledge graph. MultiDiGraph = directed edges, and allows more
# than one distinct relation between the same pair of nodes.
graph = nx.MultiDiGraph()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def embed(text):
    """Turn a string into a 768-dim vector using the embedding model."""
    return ollama.embed(model=EMBED_MODEL, input=text)['embeddings'][0]


def normalize(name):
    """Lowercase + strip whitespace so 'ACAI' and ' acai ' collapse to one node."""
    return name.strip().lower()


def chunk_text(text, chunk_size=500, stride=420):
    """
    Split text into overlapping word chunks so a fact near a chunk boundary
    doesn't get cut in half and lost. stride < chunk_size gives the overlap.
    """
    words = text.split()
    chunks = [' '.join(words[j:j + chunk_size]) for j in range(0, len(words), stride)]
    return [c for c in chunks if c]


# ---------------------------------------------------------------------------
# Ingestion: text -> vector store + knowledge graph
# ---------------------------------------------------------------------------

EXTRACT_PROMPT = """Extract factual triples from the text below.
Return ONLY a JSON array of objects with keys "subject", "relation", "object".
Text:
{text}"""


def extract_triples(text):
    """
    Ask the LLM to pull (subject, relation, object) triples out of raw text,
    constrained to JSON output. Small models sometimes return a single dict
    instead of a list, or drop a key entirely -- both are handled below.
    """
    r = ollama.chat(
        model=EXTRACT_MODEL,
        format='json',
        messages=[{'role': 'user', 'content': EXTRACT_PROMPT.format(text=text)}]
    )
    content = r['message']['content']

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        return []  # malformed output -- skip rather than crash the whole ingest

    if isinstance(result, dict):
        return [result]
    if isinstance(result, list):
        return result
    return []


def add_triple(subject, relation, obj):
    """
    Add one edge to the graph, de-duped on (subject, object, relation).
    Without this, re-ingesting the same document twice would duplicate every
    edge and pollute graph_context() with repeated facts.
    """
    s, o = normalize(subject), normalize(obj)
    if not graph.has_edge(s, o, key=relation):
        graph.add_edge(s, o, key=relation, relation=relation)


def ingest(doc_id, text):
    """
    Feed one document into both retrieval paths:
      1. Chunk + embed + store in Chroma (vector path)
      2. Extract triples + add to the graph (graph path)
    """
    # --- vector path ---
    for i, chunk in enumerate(chunk_text(text)):
        collection.add(
            ids=[f"{doc_id}_{i}"],
            embeddings=[embed(chunk)],
            documents=[chunk]
        )

    # --- graph path ---
    for t in extract_triples(text):
        s, r, o = t.get('subject'), t.get('relation'), t.get('object')
        if s and r and o:  # guard against a triple missing a key
            add_triple(s, r, o)


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def graph_context(query, hops=2):
    """
    Find entities mentioned in the query, then walk outward from each one
    up to `hops` edges (nx.ego_graph) and return every fact touched along
    the way. This is what answers multi-hop questions vector search can't.

    Uses a word-boundary regex match instead of plain substring matching,
    so a short node name like "ai" doesn't false-positive on every query
    that happens to contain those letters.
    """
    q = query.lower()
    entities = [n for n in graph.nodes if re.search(rf'\b{re.escape(n)}\b', q)]

    facts = []
    for entity in entities:
        neighborhood = nx.ego_graph(graph, entity, radius=hops)
        for u, v, data in neighborhood.edges(data=True):
            facts.append(f"{u} {data['relation']} {v}")
    return facts


def hybrid_answer(query, k=4, hops=2):
    """
    Run both retrieval paths, merge their results into one context block,
    and ask the chat model to answer using only that context.
    """
    v_chunks = collection.query(query_embeddings=[embed(query)], n_results=k)['documents'][0]
    g_facts = graph_context(query, hops=hops)

    context = "Text:\n" + "\n".join(v_chunks) + "\n\nFacts:\n" + "\n".join(g_facts)
    prompt = f"Answer using only this context:\n{context}\n\nQuestion: {query}"

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']


# ---------------------------------------------------------------------------
# Graph visualization
# ---------------------------------------------------------------------------

def show_graph(path="graph.html"):
    """
    Render the current graph as an interactive, draggable HTML file so you
    can visually check what the extractor is actually building. Open the
    output file in a browser after this runs.
    """
    net = Network(height="750px", width="100%", directed=True,
                  bgcolor="#12141a", font_color="#e8eaf0")
    net.from_nx(graph)
    for edge in net.edges:
        edge['label'] = edge.get('relation', '')
    net.show_buttons(filter_=['physics'])  # live physics/layout controls
    net.show(path, notebook=False)


def print_graph():
    """Fast text-only sanity check without opening a browser."""
    for u, v, d in graph.edges(data=True):
        print(f"{u} --[{d['relation']}]--> {v}")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ingest(
        "acai",
        "Rohan built ACAI. ACAI uses Chroma for vector storage and a decay "
        "formula for memory importance."
    )

    print_graph()
    show_graph()  # writes graph.html -- open it in a browser

    print(hybrid_answer("what does ACAI use for storage?"))