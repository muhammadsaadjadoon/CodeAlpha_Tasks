import { useEffect, useRef, useState } from 'react';
import {
  AudioLines,
  CheckCircle2,
  FileAudio2,
  Headphones,
  Info,
  Mic2,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  X,
} from 'lucide-react';
import { api } from '../api';
import { Recorder } from '../components/Recorder';
import { ResultView } from '../components/ResultView';
import type { AnalysisResult } from '../types';

function fileSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function AnalyzePage({ onAnalysisCreated }: { onAnalysisCreated: (result: AnalysisResult) => void }) {
  const [tab, setTab] = useState<'record' | 'upload'>('record');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState('');
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
  }, [previewUrl]);

  function chooseFile(file: File | undefined) {
    if (!file) return;
    setError('');

    if (file.size > 20 * 1024 * 1024) {
      setError('This file is larger than 20 MB. Please choose a shorter or compressed recording.');
      return;
    }

    if (!file.type.startsWith('audio/') && !/\.(wav|mp3|m4a|webm|ogg|flac)$/i.test(file.name)) {
      setError('Please choose a supported audio recording.');
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  }

  async function analyze(file: File | Blob, filename: string, sourceType: 'recording' | 'upload') {
    setBusy(true);
    setError('');
    try {
      const next = await api.analyze(file, filename, sourceType);
      setResult(next);
      onAnalysisCreated(next);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'The voice sample could not be analyzed.');
    } finally {
      setBusy(false);
    }
  }

  function clearUpload() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl('');
    setSelectedFile(null);
    if (input.current) input.current.value = '';
  }

  return <div className="page-stack analyze-page">
    <section className="studio-intro">
      <div className="studio-intro-copy">
        <span className="eyebrow"><AudioLines size={14}/>Emotion analysis studio</span>
        <h2>Understand how a voice feels, not only what it says.</h2>
        <p>Capture a clear speech sample and INFLECT will estimate its emotional distribution, confidence, valence, and activation.</p>
      </div>
      <div className="studio-guidance">
        <div><CheckCircle2/><span><strong>3–15 seconds</strong><small>Recommended sample length</small></span></div>
        <div><CheckCircle2/><span><strong>Natural speech</strong><small>No need to exaggerate emotion</small></span></div>
        <div><ShieldCheck/><span><strong>Private processing</strong><small>Original audio is not retained</small></span></div>
      </div>
    </section>

    <section className="analysis-workbench">
      <article className="panel capture-panel">
        <div className="capture-header">
          <div>
            <span className="section-kicker">Voice input</span>
            <h3>Choose how you want to begin</h3>
            <p>Use your microphone for a live sample or select an existing recording.</p>
          </div>
          <span className="capture-icon"><Headphones/></span>
        </div>

        <div className="input-switcher" role="tablist" aria-label="Voice input method">
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'record'}
            className={tab === 'record' ? 'active' : ''}
            onClick={() => setTab('record')}
          >
            <Mic2/><span><strong>Record live</strong><small>Use this device microphone</small></span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'upload'}
            className={tab === 'upload' ? 'active' : ''}
            onClick={() => setTab('upload')}
          >
            <UploadCloud/><span><strong>Upload audio</strong><small>Choose an existing file</small></span>
          </button>
        </div>

        <div className="capture-body">
          {tab === 'record'
            ? <Recorder busy={busy} onAnalyze={(blob, filename) => analyze(blob, filename, 'recording')}/>
            : <div className="upload-studio">
              {!selectedFile
                ? <button
                  type="button"
                  className={`dropzone ${dragging ? 'dragging' : ''}`}
                  onClick={() => input.current?.click()}
                  onDragOver={event => {
                    event.preventDefault();
                    setDragging(true);
                  }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={event => {
                    event.preventDefault();
                    setDragging(false);
                    chooseFile(event.dataTransfer.files?.[0]);
                  }}
                >
                  <span className="dropzone-icon"><UploadCloud/></span>
                  <span className="dropzone-copy">
                    <strong>Drop a recording here</strong>
                    <small>or click to choose a file from your device</small>
                  </span>
                  <span className="file-support">WAV, MP3, M4A, WebM, OGG or FLAC · Maximum 20 MB</span>
                  <input
                    ref={input}
                    hidden
                    type="file"
                    accept="audio/*,.wav,.mp3,.m4a,.webm,.ogg,.flac"
                    onChange={event => chooseFile(event.target.files?.[0])}
                  />
                </button>
                : <div className="selected-audio">
                  <div className="selected-audio-head">
                    <span className="file-icon"><FileAudio2/></span>
                    <div>
                      <strong>{selectedFile.name}</strong>
                      <span>{fileSize(selectedFile.size)} · Ready to analyze</span>
                    </div>
                    <button type="button" className="icon-button" onClick={clearUpload} aria-label="Remove selected audio">
                      <X/>
                    </button>
                  </div>
                  <audio controls preload="metadata" src={previewUrl}/>
                  <button
                    type="button"
                    className="primary-action full"
                    onClick={() => analyze(selectedFile, selectedFile.name, 'upload')}
                    disabled={busy}
                  >
                    <Sparkles/>{busy ? 'Analyzing voice…' : 'Analyze this recording'}
                  </button>
                </div>}

              <div className="privacy-note">
                <ShieldCheck/>
                <span>INFLECT temporarily processes the selected file and removes the original audio after inference.</span>
              </div>
            </div>}
        </div>

        {busy && <div className="analysis-progress" role="status" aria-live="polite">
          <span className="loading-ring"/>
          <div><strong>Analyzing emotional expression</strong><span>Conditioning the signal and comparing acoustic patterns…</span></div>
        </div>}

        {error && <div className="inline-alert danger" role="alert"><Info/>{error}</div>}
      </article>

      <article className={`panel result-panel ${result ? 'has-result' : ''}`}>
        {result
          ? <ResultView result={result}/>
          : <div className="empty-analysis">
            <div className="empty-analysis-visual">
              <div className="preview-wave" aria-hidden="true">
                {[24, 42, 66, 38, 78, 55, 31, 70, 46, 27, 58, 34].map((height, index) => <i key={index} style={{ height }}/>)}
              </div>
              <span className="preview-chip">Ready for a voice sample</span>
            </div>
            <div className="empty-analysis-copy">
              <span className="section-kicker">Your result</span>
              <h3>A clear, useful emotional profile will appear here.</h3>
              <p>Results include the leading emotion, confidence, full probability spectrum, valence, arousal, duration, and source context.</p>
              <div className="result-preview-list">
                <span><i>01</i> Dominant emotion and confidence</span>
                <span><i>02</i> Complete seven-class distribution</span>
                <span><i>03</i> Valence and activation context</span>
              </div>
            </div>
          </div>}
      </article>
    </section>
  </div>;
}
