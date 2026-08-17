import type {
    MemoryResponse,
    EpisodeResponse,
    ProcedureResponse,
} from "../types/memory";

const API_URL = "http://127.0.0.1:8000";

async function fetchData<T>(
    endpoint: string
): Promise<T> {
    const response = await fetch(
        `${API_URL}${endpoint}`
    );

    if (!response.ok) {
        throw new Error(
            `Request failed: ${response.status}`
        );
    }

    return await response.json();
}

export async function getMemories(): Promise<MemoryResponse> {
    return fetchData<MemoryResponse>("/memories");
}

export async function getEpisodes(): Promise<EpisodeResponse> {
    return fetchData<EpisodeResponse>(
        "/memories/episodes"
    );
}

export async function getProcedures(): Promise<ProcedureResponse> {
    return fetchData<ProcedureResponse>(
        "/memories/procedures"
    );
}