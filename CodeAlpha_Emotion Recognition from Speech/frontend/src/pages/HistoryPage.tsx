import { useEffect, useMemo, useState } from 'react';
import {
  CalendarDays,
  Clock3,
  Filter,
  History,
  Mic2,
  Search,
  ShieldCheck,
  Trash2,
  UploadCloud,
} from 'lucide-react';
import { api } from '../api';
import { ResultView } from '../components/ResultView';
import type { AnalysisResult } from '../types';

function titleCase(value: string) {
  return value.replace(/(^|\s)\S/g, character => character.toUpperCase());
}

export function HistoryPage({ revision }: { revision: number }) {
  const [items, setItems] = useState<AnalysisResult[]>([]);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState<AnalysisResult | null>(null);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);
    setError('');
    try {
      const page = await api.history(100, 0);
      setItems(page.items);
      setTotal(page.total);
      setSelected(current => current
        ? page.items.find(item => item.id === current.id) || null
        : page.items[0] || null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'History could not be loaded.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [revision]);

  const emotions = useMemo(
    () => Array.from(new Set(items.map(item => item.primary_emotion))).sort(),
    [items],
  );

  const filtered = useMemo(() => items.filter(item => {
    const matchesFilter = filter === 'all' || item.primary_emotion === filter;
    const needle = query.trim().toLowerCase();
    const matchesQuery = !needle
      || item.primary_emotion.toLowerCase().includes(needle)
      || item.source_name.toLowerCase().includes(needle);
    return matchesFilter && matchesQuery;
  }), [items, filter, query]);

  async function remove(id: number) {
    if (!confirm('Remove this analysis from your private history?')) return;
    await api.deleteHistory(id);
    if (selected?.id === id) setSelected(null);
    await load();
  }

  async function clearAll() {
    if (!items.length || !confirm('Clear your complete analysis history? This action cannot be undone.')) return;
    await api.clearHistory();
    setSelected(null);
    await load();
  }

  const averageConfidence = items.length
    ? Math.round(items.reduce((sum, item) => sum + item.confidence, 0) / items.length * 100)
    : 0;

  const mostCommon = items.length
    ? Object.entries(items.reduce<Record<string, number>>(
      (acc, item) => ({ ...acc, [item.primary_emotion]: (acc[item.primary_emotion] || 0) + 1 }),
      {},
    )).sort((a, b) => b[1] - a[1])[0]?.[0]
    : '—';

  return <div className="page-stack history-page">
    <section className="history-summary">
      <div>
        <span className="eyebrow"><History/>Private result archive</span>
        <h2>Every analysis, organized and easy to revisit.</h2>
        <p>INFLECT stores result metadata only. The original voice recordings are not kept.</p>
      </div>

      <div className="history-stats">
        <article><span>Total analyses</span><strong>{total}</strong></article>
        <article><span>Average confidence</span><strong>{averageConfidence}%</strong></article>
        <article><span>Most common</span><strong>{titleCase(mostCommon || '—')}</strong></article>
      </div>
    </section>

    <section className="history-layout">
      <article className="panel history-list-panel">
        <div className="history-list-header">
          <div><span className="section-kicker">Saved results</span><h3>{filtered.length} {filtered.length === 1 ? 'analysis' : 'analyses'}</h3></div>
          <button type="button" className="text-action danger" onClick={clearAll} disabled={!items.length}>
            <Trash2/>Clear all
          </button>
        </div>

        <div className="history-toolbar">
          <label className="search-field">
            <Search/>
            <input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search by emotion or source"/>
          </label>
          <label className="filter-field">
            <Filter/>
            <select value={filter} onChange={event => setFilter(event.target.value)}>
              <option value="all">All emotions</option>
              {emotions.map(emotion => <option key={emotion} value={emotion}>{titleCase(emotion)}</option>)}
            </select>
          </label>
        </div>

        {loading
          ? <div className="history-loading"><span className="loading-ring"/><span>Loading your private history…</span></div>
          : error
            ? <div className="inline-alert danger">{error}</div>
            : filtered.length
              ? <div className="history-list">
                {filtered.map(item => <button
                  type="button"
                  key={item.id}
                  className={`history-row emotion-${item.primary_emotion} ${selected?.id === item.id ? 'active' : ''}`}
                  onClick={() => setSelected(item)}
                >
                  <span className="history-emotion-mark">{item.primary_emotion.slice(0, 1).toUpperCase()}</span>
                  <span className="history-row-main">
                    <strong>{titleCase(item.primary_emotion)}</strong>
                    <small>{item.source_name}</small>
                    <span>
                      <CalendarDays/>{new Date(item.created_at).toLocaleDateString()}
                      <Clock3/>{new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </span>
                  <span className="history-row-score">
                    <strong>{Math.round(item.confidence * 100)}%</strong>
                    <small>confidence</small>
                  </span>
                  <span className="history-source-icon">
                    {item.source_type === 'recording' ? <Mic2/> : <UploadCloud/>}
                  </span>
                </button>)}
              </div>
              : <div className="empty-history">
                <span><History/></span>
                <h3>No matching analyses</h3>
                <p>New voice analyses will appear here after completion.</p>
              </div>}
      </article>

      <aside className="panel history-detail-panel">
        {selected
          ? <>
            <div className="detail-toolbar">
              <div><span className="section-kicker">Selected result</span><strong>{selected.source_name}</strong></div>
              <button type="button" className="icon-button danger" onClick={() => remove(selected.id)} aria-label="Delete analysis">
                <Trash2/>
              </button>
            </div>
            <ResultView result={selected} compact/>
          </>
          : <div className="empty-detail">
            <span className="detail-shield"><ShieldCheck/></span>
            <h3>Select an analysis</h3>
            <p>Choose a saved result to review its full emotional distribution and signal context.</p>
          </div>}
      </aside>
    </section>
  </div>;
}
