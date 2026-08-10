import type { CSSProperties } from 'react';
import {
  Activity,
  AudioLines,
  CalendarClock,
  Gauge,
  Info,
  Radio,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import type { AnalysisResult } from '../types';

const emotionCopy: Record<string, { label: string; summary: string }> = {
  angry: {
    label: 'High-intensity expression',
    summary: 'The sample carries stronger force, sharper emphasis, and elevated activation.',
  },
  disgust: {
    label: 'Aversion-oriented expression',
    summary: 'The voice pattern suggests discomfort, rejection, or pronounced disapproval.',
  },
  fear: {
    label: 'Heightened alertness',
    summary: 'The sample reflects tension, uncertainty, and increased emotional activation.',
  },
  happy: {
    label: 'Positive expression',
    summary: 'The voice carries brighter energy, warmth, and an uplifted expressive pattern.',
  },
  neutral: {
    label: 'Balanced delivery',
    summary: 'The sample remains comparatively steady, controlled, and emotionally even.',
  },
  sad: {
    label: 'Lower-energy expression',
    summary: 'The voice appears subdued, reflective, and lower in emotional activation.',
  },
  surprise: {
    label: 'Sudden activation',
    summary: 'The sample shows rapid energy shifts, heightened attention, and expressive lift.',
  },
};

function titleCase(value: string) {
  return value.replace(/(^|\s)\S/g, character => character.toUpperCase());
}

function confidenceLabel(score: number) {
  if (score >= 0.7) return 'High confidence';
  if (score >= 0.45) return 'Moderate confidence';
  return 'Low confidence';
}

function valenceLabel(value: number) {
  if (value >= 0.25) return 'More positive';
  if (value <= -0.25) return 'More negative';
  return 'Near balanced';
}

function arousalLabel(value: number) {
  if (value >= 0.65) return 'Highly activated';
  if (value >= 0.4) return 'Moderately active';
  return 'Lower activation';
}

export function ResultView({ result, compact = false }: { result: AnalysisResult; compact?: boolean }) {
  const copy = emotionCopy[result.primary_emotion] || {
    label: 'Emotional signal detected',
    summary: 'INFLECT identified a measurable emotional pattern in this sample.',
  };

  const date = new Date(result.created_at);
  const sorted = [...result.distribution].sort((a, b) => b.probability - a.probability);
  const secondary = sorted.find(item => item.label !== result.primary_emotion);
  const confidence = Math.max(0, Math.min(1, result.confidence));

  return <div className={`result-view emotion-${result.primary_emotion} ${compact ? 'compact' : ''}`}>
    <div className="result-toolbar">
      <div><Sparkles/><span>Analysis complete</span></div>
      <time>{date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</time>
    </div>

    <section className="result-summary">
      <div className="result-summary-copy">
        <span className="section-kicker">Leading emotional signal</span>
        <h2>{titleCase(result.primary_emotion)}</h2>
        <div className="result-descriptor"><TrendingUp/><strong>{copy.label}</strong></div>
        <p>{copy.summary}</p>
        {secondary && <div className="secondary-signal">
          <span>Secondary signal</span>
          <strong>{titleCase(secondary.label)}</strong>
          <small>{Math.round(secondary.probability * 100)}%</small>
        </div>}
      </div>

      <div className="confidence-card">
        <div
          className="confidence-ring"
          style={{ '--score': `${confidence * 360}deg` } as CSSProperties}
          aria-label={`${Math.round(confidence * 100)} percent confidence`}
        >
          <span>{Math.round(confidence * 100)}%</span>
        </div>
        <strong>{confidenceLabel(confidence)}</strong>
        <small>Model certainty for the leading class</small>
      </div>
    </section>

    <section className="distribution-panel">
      <div className="result-section-heading">
        <div><span className="section-kicker">Probability spectrum</span><h3>How the model distributed its confidence</h3></div>
        <AudioLines/>
      </div>
      <div className="distribution">
        {sorted.map(item => <div className="bar-row" key={item.label}>
          <span>{titleCase(item.label)}</span>
          <div className="bar-track"><i style={{ width: `${Math.max(1, item.probability * 100)}%` }}/></div>
          <b>{Math.round(item.probability * 100)}%</b>
        </div>)}
      </div>
    </section>

    <section className="signal-grid">
      <article>
        <span className="metric-icon"><Activity/></span>
        <div><span>Valence</span><strong>{result.valence.toFixed(2)}</strong><small>{valenceLabel(result.valence)}</small></div>
      </article>
      <article>
        <span className="metric-icon"><Gauge/></span>
        <div><span>Activation</span><strong>{result.arousal.toFixed(2)}</strong><small>{arousalLabel(result.arousal)}</small></div>
      </article>
      <article>
        <span className="metric-icon"><Radio/></span>
        <div><span>Signal</span><strong>{result.duration_seconds.toFixed(1)} sec</strong><small>{result.sample_rate / 1000} kHz processing rate</small></div>
      </article>
    </section>

    {!compact && <div className="result-context">
      <span><CalendarClock/>{result.source_name}</span>
      <span><ShieldCheck/>Original audio removed after inference</span>
    </div>}

    <div className="result-disclaimer">
      <Info/>
      <p>Speech emotion recognition is probabilistic and should support—not replace—human context and judgment.</p>
    </div>
  </div>;
}
