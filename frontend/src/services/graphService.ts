import type { GraphResponse } from "../types/graph";

const API_URL = "http://127.0.0.1:8000";

export async function getGraph(): Promise<GraphResponse> {
    const response = await fetch(
        `${API_URL}/graph`
    );

    if (!response.ok) {
        throw new Error(
            `Failed to load graph: ${response.status}`
        );
    }

    return await response.json();
}