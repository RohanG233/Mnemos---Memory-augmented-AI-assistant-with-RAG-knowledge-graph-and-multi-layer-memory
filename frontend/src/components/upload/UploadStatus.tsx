interface UploadStatusProps {
  loading: boolean;
  error: string | null;
  success: string | null;
}

function UploadStatus({ loading, error, success }: UploadStatusProps) {
  if (loading) {
    return (
      <div className="upload-status loading">
        <span className="loading-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
        Uploading and indexing document…
      </div>
    );
  }

  if (error) {
    return (
      <div className="upload-status error">
        ⚠ {error}
      </div>
    );
  }

  if (success) {
    return (
      <div className="upload-status success">
        ✓ {success}
      </div>
    );
  }

  return null;
}

export default UploadStatus;
