import { useEffect, useRef, useState } from 'react';
import {
  CheckCircle2,
  FileImage,
  Image as ImageIcon,
  ScanLine,
  UploadCloud,
  X,
} from 'lucide-react';

export function Dropzone({
  file,
  onFile,
}: {
  file: File | null;
  onFile: (file: File | null) => void;
}) {
  const input = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [preview, setPreview] = useState('');

  useEffect(() => {
    if (!file) {
      setPreview('');
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function accept(candidate?: File) {
    if (!candidate) return;
    if (!['image/png', 'image/jpeg', 'image/webp'].includes(candidate.type)) return;
    onFile(candidate);
  }

  if (file) {
    return (
      <div className="upload-preview">
        <div className="upload-preview-image">
          {preview ? <img src={preview} alt="Selected handwriting preview" /> : <FileImage />}
          <span className="preview-ready"><CheckCircle2 /> Ready</span>
        </div>

        <div className="upload-preview-copy">
          <span className="section-kicker">Selected image</span>
          <strong>{file.name}</strong>
          <small>{(file.size / 1024).toFixed(1)} KB · {file.type.replace('image/', '').toUpperCase()}</small>

          <div className="upload-preview-notes">
            <span><ScanLine /> Single-character crops work best</span>
            <span><ImageIcon /> Contrast is corrected automatically</span>
          </div>
        </div>

        <button className="remove-file" type="button" onClick={() => onFile(null)} aria-label="Remove selected image">
          <X />
        </button>
      </div>
    );
  }

  return (
    <div className="drop-wrap">
      <button
        type="button"
        className={`upload-dropzone ${dragging ? 'dragging' : ''}`}
        onClick={() => input.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          accept(event.dataTransfer.files[0]);
        }}
      >
        <span className="dropzone-icon"><UploadCloud /></span>
        <span className="dropzone-label">Handwriting image</span>
        <strong>Drop your character here</strong>
        <p>or choose an image from your device</p>

        <div className="dropzone-formats">
          <span>PNG</span>
          <span>JPG</span>
          <span>WEBP</span>
        </div>

        <span className="browse-button">Browse image</span>
      </button>

      <input
        ref={input}
        hidden
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={(event) => accept(event.target.files?.[0])}
      />
    </div>
  );
}
