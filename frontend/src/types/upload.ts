export interface UploadResponse {
    message: string;
    filename: string;
    chunks: number;
}

export interface UploadedDocument {
    filename: string;
    chunks: number;
}