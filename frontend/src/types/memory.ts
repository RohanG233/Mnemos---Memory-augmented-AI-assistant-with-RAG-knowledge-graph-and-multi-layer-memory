export interface Memory {
    id: string;
    content: string;
    metadata: Record<string, unknown> | null;
}

export interface MemoryResponse {
    count: number;
    memories: Memory[];
}

export interface Episode {
    id: string;
    content: string;
    metadata: Record<string, unknown> | null;
}

export interface EpisodeResponse {
    count: number;
    episodes: Episode[];
}

export interface Procedure {
    id: string;
    content: string;
    metadata: Record<string, unknown> | null;
}

export interface ProcedureResponse {
    count: number;
    procedures: Procedure[];
}