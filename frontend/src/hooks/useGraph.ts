import { useEffect, useState } from "react";

import { getGraph } from "../services/graphService";

import type {
    GraphNode,
    GraphEdge,
} from "../types/graph";

export function useGraph() {
    const [nodes, setNodes] = useState<GraphNode[]>([]);
    const [edges, setEdges] = useState<GraphEdge[]>([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(
        null
    );

    async function loadGraph() {
        setLoading(true);
        setError(null);

        try {
            const result = await getGraph();

            setNodes(result.nodes);
            setEdges(result.edges);

        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to load graph."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadGraph();
    }, []);

    return {
        nodes,
        edges,
        loading,
        error,
        reload: loadGraph,
    };
}