import type { GraphResponse } from "../types/graph";

import { apiFetch } from "./api";


export async function getGraph(
  accessToken: string | null
): Promise<GraphResponse> {

  const response = await apiFetch(
    "/graph",
    {
      method: "GET",
    },
    accessToken
  );

  if (!response.ok) {

    throw new Error(
      `Failed to load graph: ${response.status}`
    );
  }

  return await response.json();
}