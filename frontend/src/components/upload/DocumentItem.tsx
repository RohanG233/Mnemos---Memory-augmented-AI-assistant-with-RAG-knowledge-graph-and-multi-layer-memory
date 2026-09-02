import type { UploadedDocument } from "../../types/upload";

interface DocumentItemProps {
  document: UploadedDocument;
  onDelete: (documentId: string) => void;
}

function DocumentItem({ document, onDelete }: DocumentItemProps) {
  return (
    <div className="document-item">
      <div className="document-icon">📄</div>
      <div className="document-info">
        <div className="document-name">{document.filename}</div>
        <div className="document-meta">{document.chunks} chunks</div>
      </div>
      <button
        type="button"
        className="document-delete-btn"
        onClick={() => onDelete(document.document_id)}
        aria-label={`Remove ${document.filename}`}
      >
        Remove
      </button>
    </div>
  );
}

export default DocumentItem;
