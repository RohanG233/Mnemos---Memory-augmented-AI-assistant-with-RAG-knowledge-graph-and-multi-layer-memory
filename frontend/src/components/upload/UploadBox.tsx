import { useState } from "react";

interface UploadBoxProps {
  onUpload: (file: File) => void;
  loading: boolean;
}

function UploadBox({ onUpload, loading }: UploadBoxProps) {
  const [file, setFile] = useState<File | null>(null);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0];

    if (selectedFile) {
      setFile(selectedFile);
    }
  }

  function handleUpload() {
    if (!file || loading) {
      return;
    }

    onUpload(file);
  }

  return (
    <div className="upload-box">
      <input type="file" onChange={handleFileChange} disabled={loading} />

      {file && <p>Selected: {file.name}</p>}

      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
    </div>
  );
}

export default UploadBox;
