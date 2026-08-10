import {
  CheckCircle2,
  ImageIcon,
  Layers3,
  ScanSearch,
  Sparkles,
} from 'lucide-react';
import type { RecognitionResult } from '../types';

export function ResultPanel({
  result,
}: {
  result: RecognitionResult | null;
}) {
  if (!result) {
    return (
      <aside className="result-dock empty">
        <div className="result-empty-visual">
          <span className="scan-window">
            <i />
            <ScanSearch />
          </span>
        </div>

        <div className="result-empty-copy">
          <span className="section-kicker">Recognition output</span>
          <h3>Your result appears here.</h3>
          <p>
            WriteLens will show the predicted character, confidence, alternatives,
            and the normalized model input after recognition.
          </p>
        </div>

        <div className="empty-output-list">
          <span><b>01</b>Top prediction</span>
          <span><b>02</b>Candidate probabilities</span>
          <span><b>03</b>28 × 28 normalized preview</span>
        </div>
      </aside>
    );
  }

  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <aside className="result-dock has-result">
      <div className="result-status">
        <span><CheckCircle2 /> Recognition complete</span>
        <small>{result.model_role} model</small>
      </div>

      <section className="prediction-plate">
        <div className="prediction-character">
          <span>Prediction</span>
          <strong>{result.primary_label}</strong>
        </div>

        <div className="prediction-confidence">
          <span>Confidence</span>
          <strong>{confidencePercent}%</strong>
          <div className="confidence-track">
            <i style={{ width: `${Math.max(2, confidencePercent)}%` }} />
          </div>
          <small>
            {confidencePercent >= 80
              ? 'Strong model preference'
              : confidencePercent >= 55
                ? 'Moderate model preference'
                : 'Low-confidence result'}
          </small>
        </div>
      </section>

      <section className="candidate-sheet">
        <div className="result-section-title">
          <div>
            <span className="section-kicker">Probability ranking</span>
            <h3>Top candidates</h3>
          </div>
          <Layers3 />
        </div>

        <div className="candidate-list">
          {result.distribution.map((candidate, index) => (
            <div className={index === 0 ? 'leading' : ''} key={`${candidate.label}-${index}`}>
              <span className="candidate-rank">{String(index + 1).padStart(2, '0')}</span>
              <strong>{candidate.label}</strong>
              <div className="candidate-track">
                <i style={{ width: `${Math.max(2, candidate.probability * 100)}%` }} />
              </div>
              <b>{(candidate.probability * 100).toFixed(1)}%</b>
            </div>
          ))}
        </div>
      </section>

      <section className="processed-sheet">
        <div className="processed-preview">
          {result.processed_preview ? (
            <img src={result.processed_preview} alt="Normalized model input" />
          ) : (
            <ImageIcon />
          )}
        </div>

        <div className="processed-copy">
          <span className="section-kicker">Model input</span>
          <h3>Normalized handwriting</h3>
          <p>Centered, polarity-corrected and resized to the model input.</p>
          <div className="processed-tags">
            <span>28 × 28</span>
            <span>{(result.foreground_ratio * 100).toFixed(1)}% foreground</span>
          </div>
        </div>
      </section>

      <footer className="result-foot">
        <span><Sparkles /> {result.model_version}</span>
        <span>Source: {result.source_type}</span>
      </footer>
    </aside>
  );
}
