import { useEffect, useMemo, useState } from 'react';
import {
  Clock3,
  FileImage,
  History,
  Search,
  Sparkles,
  Trash2,
  TrendingUp,
} from 'lucide-react';
import { api } from '../api';
import type { RecognitionResult } from '../types';

export function HistoryPage({ revision }: { revision: number }) {
  const [items, setItems] = useState<RecognitionResult[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const page = await api.history(100, 0);
      setItems(page.items);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [revision]);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return items;
    return items.filter(
      (item) =>
        item.primary_label.toLowerCase().includes(normalized) ||
        item.source_name.toLowerCase().includes(normalized) ||
        item.model_version.toLowerCase().includes(normalized),
    );
  }, [items, query]);

  const averageConfidence = items.length
    ? items.reduce((total, item) => total + item.confidence, 0) / items.length
    : 0;

  const newest = items[0]?.created_at;

  async function remove(id: number) {
    if (!confirm('Delete this result from your backend history?')) return;
    await api.deleteHistory(id);
    load();
  }

  async function clear() {
    if (!items.length || !confirm('Clear all recognition history?')) return;
    await api.clearHistory();
    load();
  }

  return (
    <div className="wl-page history-page">
      <section className="page-hero">
        <div className="hero-copy">
          <span className="hero-index">02 · Private archive</span>
          <h1>Your recognition trail, without the original images.</h1>
          <p>
            Review predictions, confidence and model metadata. WriteLens stores result
            metadata only; the source handwriting is not retained here.
          </p>
        </div>
      </section>

      <section className="history-summary">
        <article>
          <span><History /></span>
          <div><small>Total results</small><strong>{loading ? '—' : items.length}</strong></div>
        </article>
        <article>
          <span><TrendingUp /></span>
          <div><small>Average confidence</small><strong>{loading ? '—' : `${Math.round(averageConfidence * 100)}%`}</strong></div>
        </article>
        <article>
          <span><Clock3 /></span>
          <div>
            <small>Latest activity</small>
            <strong>{newest ? new Date(newest).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '—'}</strong>
          </div>
        </article>
      </section>

      <section className="history-workspace">
        <div className="history-commandbar">
          <label className="history-search">
            <Search />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search prediction, source or model…"
            />
          </label>

          <span className="history-count">
            {filtered.length} {filtered.length === 1 ? 'result' : 'results'}
          </span>

          <button className="clear-history" type="button" onClick={clear} disabled={!items.length}>
            <Trash2 />
            Clear archive
          </button>
        </div>

        {loading ? (
          <div className="history-empty">
            <span className="loading-ring" />
            <strong>Loading your archive…</strong>
          </div>
        ) : filtered.length ? (
          <div className="history-card-grid">
            {filtered.map((item) => (
              <article className="history-result-card" key={item.id}>
                <div className="history-result-top">
                  <span className="history-character">{item.primary_label}</span>
                  <button type="button" onClick={() => remove(item.id)} aria-label="Delete recognition">
                    <Trash2 />
                  </button>
                </div>

                <div className="history-result-copy">
                  <span className="section-kicker">Prediction</span>
                  <strong>{Math.round(item.confidence * 100)}% confidence</strong>
                  <small>{item.source_name}</small>
                </div>

                <div className="history-confidence">
                  <i style={{ width: `${Math.max(2, item.confidence * 100)}%` }} />
                </div>

                <div className="history-result-meta">
                  <span><FileImage /> {item.source_type}</span>
                  <span><Sparkles /> {item.model_version}</span>
                  <span><Clock3 /> {new Date(item.created_at).toLocaleString()}</span>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="history-empty">
            <span><History /></span>
            <strong>{query ? 'No matching recognitions' : 'Your archive is empty'}</strong>
            <p>{query ? 'Try another search phrase.' : 'Character recognitions will appear here after inference.'}</p>
          </div>
        )}
      </section>
    </div>
  );
}
