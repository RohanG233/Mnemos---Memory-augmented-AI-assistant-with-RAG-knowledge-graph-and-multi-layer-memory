import json
import logging
import os

import networkx as nx

from app.core.config import GRAPH_DIRECTORY

logger = logging.getLogger(__name__)


# --------------------------------
# Graph Path
# --------------------------------

def get_graph_path(user_id: str) -> str:
    return os.path.join(GRAPH_DIRECTORY, f"{user_id}.json")


# --------------------------------
# Load Graph
# --------------------------------

def load_graph(user_id: str) -> nx.MultiDiGraph:
    """
    Load the persisted knowledge graph for a user.

    Returns an empty MultiDiGraph when:
    - no file exists yet
    - the file is corrupted / unreadable
    """

    graph_path = get_graph_path(user_id)

    if not os.path.exists(graph_path):
        return nx.MultiDiGraph()

    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return nx.node_link_graph(
            data,
            edges="edges",
            multigraph=True,
            directed=True,
        )

    except (json.JSONDecodeError, KeyError, ValueError):
        logger.warning(
            "Corrupted graph file for user=%s at %s — "
            "returning empty graph.",
            user_id,
            graph_path,
        )
        return nx.MultiDiGraph()

    except OSError:
        logger.exception("Could not read graph file for user=%s", user_id)
        return nx.MultiDiGraph()


# --------------------------------
# Save Graph
# --------------------------------

def save_graph(graph: nx.MultiDiGraph, user_id: str) -> None:
    """Persist the knowledge graph for a user."""

    graph_path = get_graph_path(user_id)

    try:
        os.makedirs(GRAPH_DIRECTORY, exist_ok=True)

        data = nx.node_link_data(graph, edges="edges")

        # Write to a temp file then rename for atomicity
        tmp_path = graph_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        os.replace(tmp_path, graph_path)

    except OSError:
        logger.exception("Could not save graph for user=%s", user_id)


# --------------------------------
# Normalize Entity
# --------------------------------

def normalize(name: str) -> str:
    return name.strip().lower()


# --------------------------------
# Convert Values
# --------------------------------

def _coerce_str(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v)
    if value is None:
        return ""
    return str(value)


# --------------------------------
# Add Triple
# --------------------------------

def add_triple(
    graph: nx.MultiDiGraph,
    subject,
    relation,
    obj,
    document_id: str | None = None,
) -> None:
    """Add a subject-relation-object triple to the graph."""

    subject = _coerce_str(subject)
    relation = _coerce_str(relation)
    obj = _coerce_str(obj)

    if not subject or not relation or not obj:
        return

    subject_n = normalize(subject)
    object_n = normalize(obj)

    # Update existing edge
    if graph.has_edge(subject_n, object_n, key=relation):
        edge_data = graph[subject_n][object_n][relation]
        document_ids = edge_data.get("document_ids", [])
        if document_id and document_id not in document_ids:
            document_ids.append(document_id)
            edge_data["document_ids"] = document_ids
        return

    # New edge
    graph.add_edge(
        subject_n,
        object_n,
        key=relation,
        relation=relation,
        document_ids=[document_id] if document_id else [],
    )


# --------------------------------
# Remove Document from Graph
# --------------------------------

def remove_document_from_graph(
    graph: nx.MultiDiGraph,
    document_id: str,
) -> None:
    """
    Remove all graph edges that were sourced exclusively
    from the given document.  Orphaned nodes are also removed.
    """

    edges_to_remove = []

    for subject, obj, relation, data in graph.edges(keys=True, data=True):
        document_ids: list = data.get("document_ids", [])

        if document_id not in document_ids:
            continue

        document_ids.remove(document_id)

        if not document_ids:
            edges_to_remove.append((subject, obj, relation))

    for subject, obj, relation in edges_to_remove:
        graph.remove_edge(subject, obj, key=relation)

    # Remove isolated nodes
    isolated = [n for n in graph.nodes if graph.degree(n) == 0]
    graph.remove_nodes_from(isolated)
