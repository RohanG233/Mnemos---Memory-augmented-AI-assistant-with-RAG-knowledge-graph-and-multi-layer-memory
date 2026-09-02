import logging

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.graph.store import load_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.get("")
def get_graph(
    user_id: str = Depends(get_current_user),
):
    graph = load_graph(user_id)

    nodes = [{"id": node} for node in graph.nodes]

    edges = [
        {
            "source": subject,
            "target": obj,
            "relation": data.get("relation", ""),
        }
        for subject, obj, data in graph.edges(data=True)
    ]

    return {"nodes": nodes, "edges": edges}
