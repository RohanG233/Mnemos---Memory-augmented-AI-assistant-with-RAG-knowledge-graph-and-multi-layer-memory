import type {
  MemoryResponse,
  EpisodeResponse,
  ProcedureResponse,
} from "../types/memory";

import { apiFetch } from "./api";


async function fetchData<T>(
  endpoint: string,
  accessToken: string | null
): Promise<T> {

  const response = await apiFetch(
    endpoint,
    {
      method: "GET",
    },
    accessToken
  );

  if (!response.ok) {

    throw new Error(
      `Request failed: ${response.status}`
    );
  }

  return await response.json();
}


export async function getMemories(
  accessToken: string | null
): Promise<MemoryResponse> {

  return fetchData<MemoryResponse>(
    "/memories",
    accessToken
  );
}


export async function getEpisodes(
  accessToken: string | null
): Promise<EpisodeResponse> {

  return fetchData<EpisodeResponse>(
    "/memories/episodes",
    accessToken
  );
}


export async function getProcedures(
  accessToken: string | null
): Promise<ProcedureResponse> {

  return fetchData<ProcedureResponse>(
    "/memories/procedures",
    accessToken
  );
}