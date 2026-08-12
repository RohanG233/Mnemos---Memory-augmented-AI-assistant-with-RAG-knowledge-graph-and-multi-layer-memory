import json
import os

import networkx as nx

from app.core.config import GRAPH_PATH


def load_graph():
    """
    Load the persisted knowledge graph.

    If no graph exists, return an empty
    directed MultiDiGraph.
    """

    if os.path.exists(GRAPH_PATH):

        with open(
            GRAPH_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return nx.node_link_graph(
            data,
            edges="edges",
            multigraph=True,
            directed=True
        )

    return nx.MultiDiGraph()


def save_graph(graph):
    """
    Persist the knowledge graph to disk.
    """

    data = nx.node_link_data(
        graph,
        edges="edges"
    )

    os.makedirs(
        os.path.dirname(GRAPH_PATH),
        exist_ok=True
    )

    with open(
        GRAPH_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


def normalize(name):
    """
    Normalize entity names before
    inserting them into the graph.
    """

    return name.strip().lower()


def _coerce_str(value):
    """
    Convert LLM output values into strings.

    Small models may occasionally return
    a list instead of a string.
    """

    if isinstance(value, list):

        return ", ".join(
            str(v)
            for v in value
            if v
        )

    if value is None:
        return ""

    return str(value)


def add_triple(
    graph,
    subject,
    relation,
    obj
):
    """
    Add a subject-relation-object triple
    to the graph.
    """

    subject = _coerce_str(subject)
    relation = _coerce_str(relation)
    obj = _coerce_str(obj)

    if not subject or not relation or not obj:
        return

    subject_normalized = normalize(
        subject
    )

    object_normalized = normalize(
        obj
    )

    if not graph.has_edge(
        subject_normalized,
        object_normalized,
        key=relation
    ):

        graph.add_edge(
            subject_normalized,
            object_normalized,
            key=relation,
            relation=relation
        )