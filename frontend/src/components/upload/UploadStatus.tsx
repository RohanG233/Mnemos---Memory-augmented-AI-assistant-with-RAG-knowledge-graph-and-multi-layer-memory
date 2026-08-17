interface UploadStatusProps {
  loading: boolean;
  error: string | null;
  success: string | null;
}

function UploadStatus({ loading, error, success }: UploadStatusProps) {
  if (loading) {
    return <p>Uploading document...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  if (success) {
    return <p>{success}</p>;
  }

  return null;
}

export default UploadStatus;
