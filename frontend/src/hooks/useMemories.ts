import { useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";

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
    const { accessToken } = useAuth();

    const [memories, setMemories] = useState<Memory[]>([]);
    const [episodes, setEpisodes] = useState<Episode[]>([]);
    const [procedures, setProcedures] = useState<Procedure[]>([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState<string | null>(
        null
    );


    async function loadMemories() {
        if (!accessToken) {
            setError("You are not authenticated.");
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const [
                memoryResponse,
                episodeResponse,
                procedureResponse,
            ] = await Promise.all([
                getMemories(accessToken),
                getEpisodes(accessToken),
                getProcedures(accessToken),
            ]);

            setMemories(
                memoryResponse.memories
            );

            setEpisodes(
                episodeResponse.episodes
            );

            setProcedures(
                procedureResponse.procedures
            );

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
    if (accessToken) {
        loadMemories();
    }
    }, [accessToken]);


    return {
        memories,
        episodes,
        procedures,
        loading,
        error,
        reload: loadMemories,
    };
}