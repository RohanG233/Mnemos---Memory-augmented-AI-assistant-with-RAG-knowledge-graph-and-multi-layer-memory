import type { UploadedDocument } from "../../types/upload";
import DocumentItem from "./DocumentItem";

interface DocumentListProps {
  documents: UploadedDocument[];
}

function DocumentList({ documents }: DocumentListProps) {
  return (
    <div className="document-list">
      <h2>Uploaded Documents</h2>

      {documents.length === 0 ? (
        <p>No documents uploaded yet.</p>
      ) : (
        documents.map((document, index) => (
          <DocumentItem
            key={`${document.filename}-${index}`}
            document={document}
          />
        ))
      )}
    </div>
  );
}

export default DocumentList;
