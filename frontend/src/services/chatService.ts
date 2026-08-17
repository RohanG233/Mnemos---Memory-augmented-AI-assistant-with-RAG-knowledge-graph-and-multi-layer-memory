import type {
    ChatRequest,
    ChatResponse,
} from "../types/chat";

const API_URL = "http://127.0.0.1:8000";

export async function sendMessage(
    message: string
): Promise<ChatResponse> {

    const request: ChatRequest = {
        message,
    };

    const response = await fetch(
        `${API_URL}/chat`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(request),
        }
    );

    if (!response.ok) {
        const error = await response.json().catch(
            () => null
        );

        throw new Error(
            error?.detail ||
            `Chat request failed: ${response.status}`
        );
    }

    return await response.json();
}