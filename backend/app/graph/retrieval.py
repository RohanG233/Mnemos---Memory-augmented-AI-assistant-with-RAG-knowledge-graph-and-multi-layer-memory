import re

import networkx as nx


def graph_context(
    graph,
    query,
    hops=2
):
    """
    Find entities mentioned in the query
    and retrieve their graph neighborhoods.
    """

    query_lower = query.lower()

    entities = [
        node
        for node in graph.nodes
        if re.search(
            rf'\b{re.escape(node)}\b',
            query_lower
        )
    ]

    facts = []

    for entity in entities:

        neighborhood = nx.ego_graph(
            graph,
            entity,
            radius=hops
        )

        for (
            subject,
            obj,
            data
        ) in neighborhood.edges(
            data=True
        ):

            facts.append(
                f"{subject} "
                f"{data['relation']} "
                f"{obj}"
            )

    return facts