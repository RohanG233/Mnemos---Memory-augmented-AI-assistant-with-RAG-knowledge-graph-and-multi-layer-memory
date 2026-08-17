export interface GraphNode {
    id: string;
}

export interface GraphEdge {
    source: string;
    target: string;
    relation: string;
}

export interface GraphResponse {
    nodes: GraphNode[];
    edges: GraphEdge[];
}