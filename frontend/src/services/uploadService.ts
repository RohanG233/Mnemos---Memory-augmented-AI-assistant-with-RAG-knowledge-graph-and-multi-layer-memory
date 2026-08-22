import type { UploadResponse } from "../types/upload";

import { apiFetch } from "./api";


export async function uploadDocument(
  file: File,
  accessToken: string | null
): Promise<UploadResponse> {

  const formData = new FormData();

  formData.append(
    "file",
    file
  );

  const response = await apiFetch(
    "/documents/upload",
    {
      method: "POST",

      body: formData,
    },
    accessToken
  );

  if (!response.ok) {

    const errorData =
      await response.json().catch(
        () => null
      );

    throw new Error(
      errorData?.detail ||
      `Upload failed: ${response.status}`
    );
  }

  return await response.json();
}