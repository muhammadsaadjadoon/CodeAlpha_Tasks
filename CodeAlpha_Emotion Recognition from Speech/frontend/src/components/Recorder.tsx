import { useEffect, useRef, useState } from 'react';
import {
  CircleStop,
  Mic,
  Play,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  TimerReset,
} from 'lucide-react';
import { Waveform } from './Waveform';

type RecorderState = 'idle' | 'requesting' | 'recording' | 'ready' | 'error';

function mergeBuffers(buffers: Float32Array[]): Float32Array {
  const length = buffers.reduce((sum, buffer) => sum + buffer.length, 0);
  const result = new Float32Array(length);
  let offset = 0;
  for (const buffer of buffers) {
    result.set(buffer, offset);
    offset += buffer.length;
  }
  return result;
}

function encodeWav(samples: Float32Array, sampleRate: number): Blob {
  const bytesPerSample = 2;
  const blockAlign = bytesPerSample;
  const buffer = new ArrayBuffer(44 + samples.length * bytesPerSample);
  const view = new DataView(buffer);

  const writeString = (offset: number, value: string) => {
    for (let index = 0; index < value.length; index += 1) {
      view.setUint8(offset + index, value.charCodeAt(index));
    }
  };

  writeString(0, 'RIFF');
  view.setUint32(4, 36 + samples.length * bytesPerSample, true);
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, 16, true);
  writeString(36, 'data');
  view.setUint32(40, samples.length * bytesPerSample, true);

  let offset = 44;
  for (const sample of samples) {
    const clamped = Math.max(-1, Math.min(1, sample));
    view.setInt16(offset, clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff, true);
    offset += 2;
  }

  return new Blob([view], { type: 'audio/wav' });
}

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remaining = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remaining}`;
}

export function Recorder({
  onAnalyze,
  busy,
}: {
  onAnalyze: (blob: Blob, filename: string) => void;
  busy: boolean;
}) {
  const [status, setStatus] = useState<RecorderState>('idle');
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);

  const streamRef = useRef<MediaStream | null>(null);
  const contextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const sinkRef = useRef<GainNode | null>(null);
  const chunksRef = useRef<Float32Array[]>([]);
  const startedAtRef = useRef(0);
  const timerRef = useRef<number | null>(null);
  const stoppingRef = useRef(false);
  const recordingRef = useRef(false);

  useEffect(() => () => cleanup(), []);
  useEffect(() => () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
  }, [audioUrl]);

  function cleanup() {
    if (timerRef.current) window.clearInterval(timerRef.current);
    timerRef.current = null;
    processorRef.current?.disconnect();
    sourceRef.current?.disconnect();
    sinkRef.current?.disconnect();
    streamRef.current?.getTracks().forEach(track => track.stop());
    contextRef.current?.close().catch(() => undefined);
    processorRef.current = null;
    sourceRef.current = null;
    sinkRef.current = null;
    streamRef.current = null;
    contextRef.current = null;
    setAnalyser(null);
  }

  async function start() {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus('error');
      setError('Live recording requires a modern browser running on localhost or HTTPS.');
      return;
    }

    setStatus('requesting');
    setError('');
    setRecordedBlob(null);
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl('');
    setDuration(0);
    chunksRef.current = [];
    stoppingRef.current = false;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      const context = new AudioContext();
      await context.resume();

      const source = context.createMediaStreamSource(stream);
      const nextAnalyser = context.createAnalyser();
      nextAnalyser.fftSize = 512;
      nextAnalyser.smoothingTimeConstant = 0.76;

      const processor = context.createScriptProcessor(4096, 1, 1);
      const sink = context.createGain();
      sink.gain.value = 0;

      processor.onaudioprocess = event => {
        if (stoppingRef.current) return;
        chunksRef.current.push(new Float32Array(event.inputBuffer.getChannelData(0)));
      };

      source.connect(nextAnalyser);
      source.connect(processor);
      processor.connect(sink);
      sink.connect(context.destination);

      streamRef.current = stream;
      contextRef.current = context;
      sourceRef.current = source;
      processorRef.current = processor;
      sinkRef.current = sink;
      setAnalyser(nextAnalyser);

      startedAtRef.current = performance.now();
      timerRef.current = window.setInterval(() => {
        const elapsed = (performance.now() - startedAtRef.current) / 1000;
        setDuration(elapsed);
        if (elapsed >= 30) stop();
      }, 100);

      recordingRef.current = true;
      setStatus('recording');
    } catch (reason) {
      cleanup();
      setStatus('error');
      const name = reason instanceof DOMException ? reason.name : '';
      setError(
        name === 'NotAllowedError'
          ? 'Microphone access is blocked. Allow permission in your browser and try again.'
          : name === 'NotFoundError'
            ? 'No microphone was detected on this device.'
            : 'The microphone could not be started. Close other applications using it and try again.',
      );
    }
  }

  function stop() {
    if (!recordingRef.current || stoppingRef.current) return;

    stoppingRef.current = true;
    recordingRef.current = false;
    const context = contextRef.current;
    const samples = mergeBuffers(chunksRef.current);
    const sampleRate = context?.sampleRate || 48000;
    cleanup();

    if (samples.length === 0) {
      setStatus('error');
      setError('No voice signal was captured. Please record another sample.');
      return;
    }

    const blob = encodeWav(samples, sampleRate);
    const url = URL.createObjectURL(blob);
    setRecordedBlob(blob);
    setAudioUrl(url);
    setDuration(samples.length / sampleRate);
    setStatus('ready');
  }

  function reset() {
    cleanup();
    recordingRef.current = false;
    setStatus('idle');
    setError('');
    setDuration(0);
    setRecordedBlob(null);
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl('');
    chunksRef.current = [];
  }

  const statusCopy = status === 'recording'
    ? 'Recording in progress'
    : status === 'requesting'
      ? 'Connecting to microphone'
      : status === 'ready'
        ? 'Recording ready'
        : status === 'error'
          ? 'Microphone unavailable'
          : 'Ready to record';

  return <div className="recorder-studio">
    <div className={`recorder-console state-${status}`}>
      <div className="recorder-console-top">
        <div className="recorder-status">
          <span className={`status-dot ${status === 'recording' ? 'live' : ''}`}/>
          <span>{statusCopy}</span>
        </div>
        <div className="recording-clock"><TimerReset/><strong>{formatTime(duration)}</strong><small>/ 00:30</small></div>
      </div>

      <div className="waveform-stage">
        <Waveform analyser={analyser} active={status === 'recording'}/>
        <div className="waveform-baseline" aria-hidden="true"/>
      </div>

      <div className="recorder-center-action">
        {status !== 'recording' && status !== 'ready'
          ? <button
            type="button"
            className="mic-control"
            onClick={start}
            disabled={status === 'requesting' || busy}
            aria-label="Begin recording"
          >
            <span><Mic/></span>
            <strong>{status === 'requesting' ? 'Connecting…' : 'Start recording'}</strong>
          </button>
          : status === 'recording'
            ? <button type="button" className="mic-control stop" onClick={stop} aria-label="Finish recording">
              <span><CircleStop/></span>
              <strong>Finish recording</strong>
            </button>
            : <div className="recording-complete">
              <span><Play/></span>
              <div><strong>Sample captured</strong><small>Listen once before analysis</small></div>
            </div>}
      </div>

      <div className="recorder-hint">
        {status === 'recording'
          ? 'Speak naturally. A clear sentence with steady volume works best.'
          : status === 'ready'
            ? 'Review the sample below, then continue to emotional analysis.'
            : 'Use a quiet space and keep the microphone approximately 15–30 cm away.'}
      </div>
    </div>

    {status === 'ready' && audioUrl && <div className="recording-review">
      <div className="recording-review-head">
        <div><span className="section-kicker">Recorded sample</span><strong>{formatTime(duration)} captured</strong></div>
        <button type="button" className="text-action" onClick={reset} disabled={busy}><RotateCcw/>Record again</button>
      </div>
      <audio controls preload="metadata" src={audioUrl}/>
      <button
        type="button"
        className="primary-action full"
        onClick={() => recordedBlob && onAnalyze(recordedBlob, `inflect-recording-${Date.now()}.wav`)}
        disabled={!recordedBlob || busy}
      >
        <Sparkles/>{busy ? 'Analyzing voice…' : 'Analyze this recording'}
      </button>
    </div>}

    {error && <div className="inline-alert danger" role="alert">{error}</div>}

    <div className="privacy-note compact">
      <ShieldCheck/>
      <span>Original audio is processed temporarily and removed after inference. Only result metadata is retained in your private history.</span>
    </div>
  </div>;
}
