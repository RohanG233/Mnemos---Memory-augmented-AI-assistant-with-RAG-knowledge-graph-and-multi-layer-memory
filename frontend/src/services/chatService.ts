import type {
  ChatRequest,
  ChatResponse,
} from "../types/chat";

import { apiFetch } from "./api";


export async function sendMessage(
  message: string,
  accessToken: string | null
): Promise<ChatResponse> {

  const request: ChatRequest = {
    message,
  };

  const response = await apiFetch(
    "/chat",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(request),
    },
    accessToken
  );

  if (!response.ok) {

    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ||
      `Chat request failed: ${response.status}`
    );
  }

  return await response.json();
}