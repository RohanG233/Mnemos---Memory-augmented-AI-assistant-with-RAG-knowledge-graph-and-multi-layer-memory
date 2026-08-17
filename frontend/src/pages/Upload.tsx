import UploadBox from "../components/upload/UploadBox";
import UploadStatus from "../components/upload/UploadStatus";
import DocumentList from "../components/upload/DocumentList";
import { useUpload } from "../hooks/useUpload";

function Upload() {
  const { upload, documents, loading, error, success } = useUpload();

  return (
    <main>
      <h1>Documents</h1>

      <UploadBox onUpload={upload} loading={loading} />

      <UploadStatus loading={loading} error={error} success={success} />

      <DocumentList documents={documents} />
    </main>
  );
}

export default Upload;
