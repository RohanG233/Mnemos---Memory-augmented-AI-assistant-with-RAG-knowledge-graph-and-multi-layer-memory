import type { UploadResponse } from "../types/upload";

const API_URL = "http://127.0.0.1:8000";

export async function uploadDocument(
    file: File
): Promise<UploadResponse> {
    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
            errorData?.detail ||
            `Upload failed: ${response.status}`
        );
    }

    return await response.json();
}