import { useEffect, useState } from "react";

import {
    getMemories,
    getEpisodes,
    getProcedures,
} from "../services/memoryService";

import type {
    Memory,
    Episode,
    Procedure,
} from "../types/memory";

export function useMemories() {
    const [memories, setMemories] = useState<Memory[]>([]);
    const [episodes, setEpisodes] = useState<Episode[]>([]);
    const [procedures, setProcedures] = useState<Procedure[]>([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function loadMemories() {
        setLoading(true);
        setError(null);

        try {
            const [
                memoryResponse,
                episodeResponse,
                procedureResponse,
            ] = await Promise.all([
                getMemories(),
                getEpisodes(),
                getProcedures(),
            ]);

            setMemories(memoryResponse.memories);
            setEpisodes(episodeResponse.episodes);
            setProcedures(procedureResponse.procedures);

        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to load memories."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadMemories();
    }, []);

    return {
        memories,
        episodes,
        procedures,
        loading,
        error,
        reload: loadMemories,
    };
}