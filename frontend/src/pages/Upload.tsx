import UploadBox from "../components/upload/UploadBox";
import UploadStatus from "../components/upload/UploadStatus";
import DocumentList from "../components/upload/DocumentList";
import { useUpload } from "../hooks/useUpload";

function Upload() {
  const { upload, documents, loading, error, success, removeDocument } = useUpload();

  return (
    <main className="upload-page">
      <div className="page-header">
        <h1>Documents</h1>
      </div>

      <UploadBox onUpload={upload} loading={loading} />

      <UploadStatus loading={loading} error={error} success={success} />

      <DocumentList documents={documents} onDelete={removeDocument} />
    </main>
  );
}

export default Upload;
