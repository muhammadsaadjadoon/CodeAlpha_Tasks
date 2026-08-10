import { useState } from 'react';
import {
  ArrowRight,
  ImageUp,
  LockKeyhole,
  PenTool,
  ScanText,
  Sparkles,
} from 'lucide-react';
import { api } from '../api';
import { DrawingPad } from '../components/DrawingPad';
import { Dropzone } from '../components/Dropzone';
import { ResultPanel } from '../components/ResultPanel';
import type { RecognitionResult } from '../types';

export function RecognizePage({
  onCreated,
}: {
  onCreated: () => void;
}) {
  const [source, setSource] = useState<'upload' | 'draw'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [drawBlob, setDrawBlob] = useState<Blob | null>(null);
  const [mode, setMode] = useState('auto');
  const [result, setResult] = useState<RecognitionResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const input = source === 'upload' ? file : drawBlob;
  const ready = Boolean(input);

  async function recognize() {
    if (!input) return;

    setBusy(true);
    setError('');

    try {
      const response = await api.recognize(
        input,
        source === 'upload' ? file?.name || 'handwriting.png' : 'canvas-character.png',
        mode,
        source,
      );
      setResult(response);
      onCreated();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Recognition failed.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="wl-page recognize-page">
      <section className="page-hero recognize-hero">
        <div className="hero-copy">
          <span className="hero-index">01 · Recognition studio</span>
          <h1>Read a handwritten character in seconds.</h1>
          <p>
            Upload an image or write directly on the canvas. The input is cleaned,
            centered, normalized and passed to the selected CNN model.
          </p>
        </div>

        <div className="recognize-hero-badge">
          <span><LockKeyhole /> Private input</span>
          <strong>Original images are not added to history.</strong>
        </div>
      </section>

      <section className="recognition-layout">
        <article className="studio-board">
          <div className="studio-board-head">
            <div>
              <span className="section-kicker">Input workspace</span>
              <h2>Prepare your handwriting</h2>
            </div>

            <label className="mode-select">
              <span>Recognition mode</span>
              <select value={mode} onChange={(event) => setMode(event.target.value)}>
                <option value="auto">Auto / Characters</option>
                <option value="characters">Characters</option>
                <option value="digits">Digits only</option>
              </select>
            </label>
          </div>

          <div className="input-methods">
            <button
              type="button"
              className={source === 'upload' ? 'active' : ''}
              onClick={() => setSource('upload')}
            >
              <span><ImageUp /></span>
              <div>
                <strong>Upload image</strong>
                <small>Use an existing photo or crop</small>
              </div>
            </button>

            <button
              type="button"
              className={source === 'draw' ? 'active' : ''}
              onClick={() => setSource('draw')}
            >
              <span><PenTool /></span>
              <div>
                <strong>Draw directly</strong>
                <small>Write with mouse, touch or pen</small>
              </div>
            </button>
          </div>

          <div className="studio-source">
            {source === 'upload' ? (
              <Dropzone file={file} onFile={setFile} />
            ) : (
              <DrawingPad onBlob={setDrawBlob} />
            )}
          </div>

          {error && <div className="form-error recognition-error">{error}</div>}

          <div className="studio-action-row">
            <div className="studio-security">
              <LockKeyhole />
              <span>
                <strong>Ephemeral processing</strong>
                <small>The raw handwriting image is discarded after this request.</small>
              </span>
            </div>

            <button
              type="button"
              className="recognize-action"
              onClick={recognize}
              disabled={!ready || busy}
            >
              <span className="recognize-action-icon">{busy ? <Sparkles /> : <ScanText />}</span>
              <span>
                <small>{busy ? 'CNN is processing' : ready ? 'Input ready' : 'Add handwriting first'}</small>
                <strong>{busy ? 'Recognizing…' : 'Recognize character'}</strong>
              </span>
              <ArrowRight />
            </button>
          </div>
        </article>

        <ResultPanel result={result} />
      </section>
    </div>
  );
}
