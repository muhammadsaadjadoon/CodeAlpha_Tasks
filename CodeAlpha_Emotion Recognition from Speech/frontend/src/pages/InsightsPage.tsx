import {
  Activity,
  BrainCircuit,
  Database,
  Gauge,
  Layers3,
  RadioTower,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import type { ModelStatus } from '../types';

const architecture = [
  {
    icon: BrainCircuit,
    title: 'Dual acoustic ensemble',
    text: 'Two calibrated RBF experts evaluate timbre, energy, rhythm, and spectral movement before combining probabilities.',
  },
  {
    icon: Database,
    title: 'RAVDESS with augmentation',
    text: 'The included champion uses 1,440 unique actor recordings and label-preserving synthetic variation for stronger coverage.',
  },
  {
    icon: Layers3,
    title: 'Speaker-separated evaluation',
    text: 'Actor identities remain separated across training, validation, and test splits to reduce information leakage.',
  },
  {
    icon: Gauge,
    title: 'Transparent model reporting',
    text: 'Macro F1, unweighted average recall, class-level metrics, and a held-out actor test set document performance honestly.',
  },
];

export function InsightsPage({ modelStatus }: { modelStatus: ModelStatus | null }) {
  const statusTitle = modelStatus?.ready
    ? 'Local champion ready'
    : modelStatus?.state === 'error'
      ? 'Model requires attention'
      : 'Model available';

  return <div className="page-stack insights-page">
    <section className="insights-hero">
      <div>
        <span className="eyebrow"><Sparkles/>Model transparency</span>
        <h2>Understand what powers every INFLECT result.</h2>
        <p>A practical view of the training foundation, inference pipeline, evaluation strategy, and privacy safeguards.</p>
      </div>
      <div className={`model-status-card state-${modelStatus?.state || 'loading'}`}>
        <span className="status-pulse"/>
        <div><strong>{statusTitle}</strong><small>{modelStatus?.message || 'Checking model readiness…'}</small></div>
      </div>
    </section>

    <section className="panel model-overview">
      <div className="model-overview-copy">
        <span className="section-kicker">Current inference engine</span>
        <h3>{modelStatus?.model_version === 'Not loaded'
          ? 'INFLECT emotion classifier'
          : modelStatus?.model_version || 'INFLECT emotion classifier'}</h3>
        <p>The included champion runs locally, averages evidence across voice segments, and does not require a third-party inference service.</p>
      </div>
      <div className="model-specs">
        <span><RadioTower/><small>Compute</small><strong>{modelStatus?.device || 'CPU'}</strong></span>
        <span><Activity/><small>Signal rate</small><strong>16 kHz</strong></span>
        <span><ShieldCheck/><small>Audio handling</small><strong>Transient</strong></span>
      </div>
    </section>

    <section className="insight-grid">
      {architecture.map(({ icon: Icon, title, text }, index) => <article className="panel insight-card" key={title}>
        <div className="insight-card-top"><span className="insight-icon"><Icon/></span><span className="insight-number">0{index + 1}</span></div>
        <h3>{title}</h3>
        <p>{text}</p>
      </article>)}
    </section>

    <section className="panel pipeline-panel">
      <div className="pipeline-header">
        <div><span className="section-kicker">Inference workflow</span><h3>From speech to emotional probabilities</h3></div>
        <BrainCircuit/>
      </div>
      <div className="pipeline-flow">
        <article><span>01</span><strong>Capture</strong><small>Live microphone or uploaded recording</small></article>
        <i/>
        <article><span>02</span><strong>Condition</strong><small>Mono conversion, resampling, normalization</small></article>
        <i/>
        <article><span>03</span><strong>Represent</strong><small>Spectral, temporal, and prosodic features</small></article>
        <i/>
        <article><span>04</span><strong>Infer</strong><small>Calibrated probability fusion, valence, arousal</small></article>
      </div>
    </section>

    <section className="insights-note">
      <ShieldCheck/>
      <div><strong>Important context</strong><p>Emotion recognition estimates acoustic expression. It does not determine intent, truthfulness, mental health, or identity.</p></div>
    </section>
  </div>;
}
