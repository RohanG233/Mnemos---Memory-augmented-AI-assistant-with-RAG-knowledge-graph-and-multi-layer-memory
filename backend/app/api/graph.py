from fastapi import APIRouter

from app.main import graph


router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"]
)


@router.get("")
def get_graph():

    nodes = []

    for node in graph.nodes:

        nodes.append({
            "id": node
        })


    edges = []

    for (
        subject,
        obj,
        data
    ) in graph.edges(
        data=True
    ):

        edges.append({
            "source": subject,
            "target": obj,
            "relation":
                data.get(
                    "relation",
                    ""
                )
        })


    return {
        "nodes": nodes,
        "edges": edges
    }