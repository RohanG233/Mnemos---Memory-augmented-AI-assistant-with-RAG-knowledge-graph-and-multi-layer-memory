export interface UploadResponse {
  message: string;
  document_id: string;
  filename: string;
  chunks: number;
}

export interface UploadedDocument {
  document_id: string;
  filename: string;
  chunks: number;
}