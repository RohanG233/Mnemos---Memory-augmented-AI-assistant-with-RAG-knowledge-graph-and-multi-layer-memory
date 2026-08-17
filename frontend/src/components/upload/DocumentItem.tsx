import type { UploadedDocument } from "../../types/upload";

interface DocumentItemProps {
  document: UploadedDocument;
}

function DocumentItem({ document }: DocumentItemProps) {
  return (
    <div className="document-item">
      <div>
        <strong>📄 {document.filename}</strong>

        <p>{document.chunks} chunks</p>
      </div>
    </div>
  );
}

export default DocumentItem;
