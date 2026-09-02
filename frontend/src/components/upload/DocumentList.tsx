import type { UploadedDocument } from "../../types/upload";
import DocumentItem from "./DocumentItem";

interface DocumentListProps {
  documents: UploadedDocument[];
  onDelete: (documentId: string) => void;
}

function DocumentList({ documents, onDelete }: DocumentListProps) {
  return (
    <div className="document-list-section">
      <h2 className="memory-section-title">
        Uploaded Documents ({documents.length})
      </h2>

      {documents.length === 0 ? (
        <div className="empty-state">
          <h3>No documents yet</h3>
          <p>Upload a .txt file above to add it to your knowledge base.</p>
        </div>
      ) : (
        <div className="document-list">
          {documents.map((doc) => (
            <DocumentItem key={doc.document_id} document={doc} onDelete={onDelete} />
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentList;
