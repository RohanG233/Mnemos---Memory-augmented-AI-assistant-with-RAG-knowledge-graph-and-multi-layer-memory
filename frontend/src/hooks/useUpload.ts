import { useState } from "react";

import { useAuth } from "../context/AuthContext";

import { uploadDocument } from "../services/uploadService";

import type { UploadedDocument } from "../types/upload";


export function useUpload() {
    const { accessToken } = useAuth();

    const [documents, setDocuments] = useState<
        UploadedDocument[]
    >([]);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState<string | null>(
        null
    );

    const [success, setSuccess] = useState<string | null>(
        null
    );


    async function upload(file: File) {
        if (!accessToken) {
            setError("You are not authenticated.");
            return;
        }

        setError(null);
        setSuccess(null);
        setLoading(true);

        try {
            const response = await uploadDocument(
                file,
                accessToken
            );

            const document: UploadedDocument = {
                filename: response.filename,
                chunks: response.chunks,
            };

            setDocuments((previousDocuments) => [
                ...previousDocuments,
                document,
            ]);

            setSuccess(response.message);

        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Upload failed."
            );
        } finally {
            setLoading(false);
        }
    }


    return {
        documents,
        upload,
        loading,
        error,
        success,
    };
}