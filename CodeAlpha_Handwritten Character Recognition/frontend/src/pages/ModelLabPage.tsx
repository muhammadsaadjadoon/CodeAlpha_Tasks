import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  BrainCircuit,
  CheckCircle2,
  CircleDashed,
  Cpu,
  Database,
  FlaskConical,
  Layers3,
  Network,
} from 'lucide-react';
import { api } from '../api';
import type { ModelStatus } from '../types';

export function ModelLabPage() {
  const [status, setStatus] = useState<ModelStatus>({});
  const [metrics, setMetrics] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.modelStatus().then(setStatus),
      api.modelMetrics().then((value) => setMetrics(value as Record<string, any>)),
    ])
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const readyCount = useMemo(
    () => Object.values(status).filter((model) => model.ready).length,
    [status],
  );

  return (
    <div className="wl-page model-page">
      <section className="page-hero">
        <div className="hero-copy">
          <span className="hero-index">03 · Model laboratory</span>
          <h1>See exactly which handwriting models are ready.</h1>
          <p>
            No fake readiness. This page reflects the actual registered checkpoints and
            evaluation reports produced by your MNIST and EMNIST training pipeline.
          </p>
        </div>

        <div className="model-ready-summary">
          <span className={readyCount ? 'ready' : 'pending'}>
            {readyCount ? <CheckCircle2 /> : <CircleDashed />}
          </span>
          <div>
            <small>Registered checkpoints</small>
            <strong>{loading ? 'Checking…' : `${readyCount} ready`}</strong>
          </div>
        </div>
      </section>

      <section className="model-registry">
        {Object.entries(status).map(([role, model]) => {
          const modelMetrics = metrics[role];
          return (
            <article className="model-registry-card" key={role}>
              <header>
                <span className="model-role-icon"><BrainCircuit /></span>
                <div>
                  <span className="section-kicker">{role} specialist</span>
                  <h2>{model.name}</h2>
                </div>
                <span className={`checkpoint-state ${model.ready ? 'ready' : 'pending'}`}>
                  {model.ready ? <CheckCircle2 /> : <CircleDashed />}
                  {model.ready ? 'Ready' : 'Missing'}
                </span>
              </header>

              <div className="model-registry-body">
                <div className="model-info-list">
                  <span><Cpu /><small>Checkpoint</small><strong>{model.ready ? 'TorchScript available' : 'Train required'}</strong></span>
                  <span><Database /><small>Evaluation</small><strong>{model.metrics_available ? 'Metrics available' : 'Pending'}</strong></span>
                  <span><Layers3 /><small>Role</small><strong>{role === 'digit' ? '0–9 digits' : 'Full characters'}</strong></span>
                </div>

                <div className="model-scoreboard">
                  <article>
                    <small>Accuracy</small>
                    <strong>{modelMetrics ? `${(modelMetrics.accuracy * 100).toFixed(1)}%` : '—'}</strong>
                  </article>
                  <article>
                    <small>Macro F1</small>
                    <strong>{modelMetrics ? `${(modelMetrics.macro_f1 * 100).toFixed(1)}%` : '—'}</strong>
                  </article>
                  <article>
                    <small>UAR</small>
                    <strong>{modelMetrics ? `${(modelMetrics.uar * 100).toFixed(1)}%` : '—'}</strong>
                  </article>
                </div>
              </div>
            </article>
          );
        })}

        {!loading && !Object.keys(status).length && (
          <div className="model-empty">
            <FlaskConical />
            <strong>No model registry was returned.</strong>
            <p>Run the training and registration commands in COMMANDS.md.</p>
          </div>
        )}
      </section>

      <section className="training-map">
        <div className="training-map-copy">
          <span className="section-kicker">Training architecture</span>
          <h2>A professional path from dataset to deployable checkpoint.</h2>
          <p>
            Training stays separate from the web request path, so inference is fast and
            model evidence remains reproducible.
          </p>
        </div>

        <div className="training-map-flow">
          <article><span>01</span><Database /><strong>Datasets</strong><small>MNIST · EMNIST Balanced · EMNIST ByClass</small></article>
          <i />
          <article><span>02</span><Activity /><strong>Preparation</strong><small>Augmentation · weights · validation split</small></article>
          <i />
          <article><span>03</span><Network /><strong>CNN training</strong><small>AdamW · OneCycle · early stopping</small></article>
          <i />
          <article><span>04</span><Cpu /><strong>Deployment</strong><small>Evaluation · TorchScript · registry</small></article>
        </div>
      </section>
    </div>
  );
}
