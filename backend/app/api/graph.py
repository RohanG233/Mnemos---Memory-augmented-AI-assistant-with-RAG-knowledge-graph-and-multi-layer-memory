from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.main import graph


router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"]
)


@router.get("")
def get_graph(user_id: str = Depends(get_current_user)):

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