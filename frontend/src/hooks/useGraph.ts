import { useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";

import { getGraph } from "../services/graphService";

import type {
    GraphNode,
    GraphEdge,
} from "../types/graph";


export function useGraph() {
    const { accessToken } = useAuth();

    const [nodes, setNodes] = useState<GraphNode[]>([]);

    const [edges, setEdges] = useState<GraphEdge[]>([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState<string | null>(
        null
    );


    async function loadGraph() {
        if (!accessToken) {
            setError("You are not authenticated.");
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const result = await getGraph(
                accessToken
            );

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
    if (accessToken) {
        loadGraph();
    }
    }, [accessToken]);


    return {
        nodes,
        edges,
        loading,
        error,
        reload: loadGraph,
    };
}