import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useSession } from '../context/SessionContext.jsx'
import { Icon } from '../components/Icons.jsx'

function pct(v) { return Number.isFinite(v) ? `${(v * 100).toFixed(1)}%` : '—' }

export default function Overview() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { cases } = useSession()
  const [health, setHealth] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [dataset, setDataset] = useState(null)

  useEffect(() => {
    Promise.allSettled([api.health(), api.modelReport(), api.datasetReport()]).then(([h, m, d]) => {
      if (h.status === 'fulfilled') setHealth(h.value)
      if (m.status === 'fulfilled') setMetrics(m.value)
      if (d.status === 'fulfilled') setDataset(d.value)
    })
  }, [])

  const holdout = metrics?.calibrated_holdout || {}
  const selected = metrics?.selected_model || 'Loading model…'
  const topModels = metrics?.models ? Object.entries(metrics.models).sort((a,b) => b[1].cv_roc_auc - a[1].cv_roc_auc).slice(0,4) : []

  return (
    <div className="page-stack">
      <section className="command-hero">
        <div className="command-hero__copy">
          <div className="status-line"><span className="status-line__dot"/>Ready for assessment</div>
          <h2>Welcome back, {user?.display_name?.split(' ')[0] || 'there'}.</h2>
          <p>Start a new assessment, review model performance, or revisit results from this session.</p>
          <div className="hero-actions">
            <button className="btn btn--primary" onClick={() => navigate('/app/assessment')}><Icon name="plus" size={17}/>New assessment</button>
            <button className="btn btn--ghost" onClick={() => navigate('/app/models')}>View model performance <Icon name="arrow" size={17}/></button>
          </div>
        </div>
        <div className="command-hero__signal" aria-hidden="true">
          <div className="ecg-grid" />
          <svg viewBox="0 0 520 160" preserveAspectRatio="none"><path className="ecg-path-shadow" d="M0 86h80l18-2 18-42 22 88 21-49 19 5h64l17-3 18-27 17 58 17-34 18 6h72l18-4 14-19 14 40 16-26 18 5h58"/><path className="ecg-path" d="M0 86h80l18-2 18-42 22 88 21-49 19 5h64l17-3 18-27 17 58 17-34 18 6h72l18-4 14-19 14 40 16-26 18 5h58"/></svg>
          <div className="signal-readout"><span>MODEL</span><strong>{health?.model_ready ? 'Ready' : 'Checking'}</strong><small>{selected}</small></div>
        </div>
      </section>

      <section className="metric-strip">
        <article><span className="metric-strip__icon"><Icon name="brain"/></span><div><small>Active model</small><strong>{selected}</strong></div><em>best cross-validation score</em></article>
        <article><span className="metric-strip__icon"><Icon name="activity"/></span><div><small>Model ROC-AUC</small><strong>{holdout.roc_auc?.toFixed(4) || '—'}</strong></div><em>{pct(holdout.roc_auc)} test performance</em></article>
        <article><span className="metric-strip__icon"><Icon name="database"/></span><div><small>Training records</small><strong>{dataset?.rows || '—'}</strong></div><em>{dataset?.features || 13} clinical inputs</em></article>
        <article><span className="metric-strip__icon"><Icon name="users"/></span><div><small>Session assessments</small><strong>{cases.length}</strong></div><em>this session</em></article>
      </section>

      <div className="dashboard-grid">
        <section className="panel panel--wide">
          <div className="panel-head"><div><span className="section-kicker">MODEL PERFORMANCE</span><h3>Model comparison</h3></div><button className="text-btn" onClick={() => navigate('/app/models')}>View all models <Icon name="arrow" size={15}/></button></div>
          <div className="model-rows">
            {topModels.length ? topModels.map(([name, info], index) => (
              <div className="model-row" key={name}><span className={`model-rank ${index === 0 ? 'model-rank--best' : ''}`}>{String(index+1).padStart(2,'0')}</span><div className="model-row__name"><strong>{name}</strong><small>{index === 0 ? 'Best cross-validation score' : 'Compared model'}</small></div><div className="score-track"><span style={{ width: `${Math.max(5, info.cv_roc_auc*100)}%` }}/></div><strong className="model-row__score">{info.cv_roc_auc.toFixed(4)}</strong></div>
            )) : <div className="skeleton-list"><span/><span/><span/><span/></div>}
          </div>
        </section>

        <section className="panel">
          <div className="panel-head"><div><span className="section-kicker">ASSESSMENT FLOW</span><h3>From patient details to result</h3></div></div>
          <div className="pipeline-list">
            {['Enter patient details','Review your entries','Calculate risk','Review the result'].map((x,i) => <div key={x}><span>{i+1}</span><p><strong>{x}</strong><small>{['Complete all 13 assessment fields','HeartTrack checks each value','The trained model estimates probability','See the risk level and key factors'][i]}</small></p></div>)}
          </div>
          <button className="panel-action" onClick={() => navigate('/app/assessment')}>Start assessment <Icon name="chevron" size={16}/></button>
        </section>

        <section className="panel">
          <div className="panel-head"><div><span className="section-kicker">TRAINING DATA</span><h3>Records by source</h3></div></div>
          <div className="cohort-bars">
            {dataset?.source_counts ? Object.entries(dataset.source_counts).map(([name,count]) => <div key={name}><div><span>{name}</span><strong>{count}</strong></div><div className="cohort-track"><span style={{width:`${count/dataset.rows*100}%`}}/></div></div>) : <div className="skeleton-list"><span/><span/><span/></div>}
          </div>
          <div className="panel-foot-stat"><span>Records with disease indication</span><strong>{pct(dataset?.positive_rate)}</strong></div>
        </section>

        <section className="panel panel--wide overview-privacy-panel">
          <div className="panel-head"><div><span className="section-kicker">PRIVACY</span><h3>How your session works</h3></div></div>
          <div className="privacy-flow"><div><Icon name="user"/><strong>Your browser</strong><small>Your entries stay on this page</small></div><span>→</span><div><Icon name="shield"/><strong>Secure sign-in</strong><small>Your account stays protected</small></div><span>→</span><div><Icon name="activity"/><strong>Secure processing</strong><small>Your assessment is handled securely</small></div><span>→</span><div><Icon name="brain"/><strong>Prediction model</strong><small>Returns an estimated risk</small></div></div>
        </section>
      </div>
    </div>
  )
}
