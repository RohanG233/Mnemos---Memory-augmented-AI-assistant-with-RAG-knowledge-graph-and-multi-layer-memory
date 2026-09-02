import { useRef, useState } from "react";

interface UploadBoxProps {
  onUpload: (file: File) => void;
  loading: boolean;
}

function UploadBox({ onUpload, loading }: UploadBoxProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) setFile(f);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) setFile(f);
  }

  function handleUpload() {
    if (!file || loading) return;
    onUpload(file);
    setFile(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div
      className={`upload-dropzone${dragOver ? " drag-over" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <div className="upload-dropzone-icon">📂</div>
      <h3>Drop a .txt file here</h3>
      <p>or click to browse your files</p>

      <input
        ref={inputRef}
        type="file"
        accept=".txt"
        onChange={handleFileChange}
        disabled={loading}
        onClick={(e) => e.stopPropagation()}
      />

      {file ? (
        <div
          className="upload-selected-file"
          onClick={(e) => e.stopPropagation()}
        >
          <span>📄</span>
          <span className="upload-selected-file-name">{file.name}</span>
          <button
            type="button"
            className="btn btn-primary"
            onClick={(e) => { e.stopPropagation(); handleUpload(); }}
            disabled={loading}
            style={{ marginLeft: "auto", padding: "7px 16px", fontSize: 13 }}
          >
            {loading ? "Uploading…" : "Upload"}
          </button>
        </div>
      ) : (
        <span className="upload-file-label" onClick={(e) => e.stopPropagation()}>
          📁 Choose file
        </span>
      )}
    </div>
  );
}

export default UploadBox;
