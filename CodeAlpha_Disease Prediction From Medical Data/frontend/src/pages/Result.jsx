import { Navigate, useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext.jsx'
import { Icon } from '../components/Icons.jsx'

const directionLabel = { higher: 'Raises estimate', lower: 'Lowers estimate', neutral: 'Little effect' }

function riskClass(level='Low') { return `risk-${level.toLowerCase().replace(' ','-')}` }

export default function Result() {
  const { lastResult } = useSession()
  const navigate = useNavigate()
  if (!lastResult) return <Navigate to="/app/assessment" replace />
  const { result, input, id, createdAt } = lastResult
  const percent = Number(result.percent ?? result.probability*100)

  return <div className="result-page">
    <div className="result-topline"><div><span className="section-kicker">CASE {id}</span><h2>Your risk result is ready</h2><p>{new Date(createdAt).toLocaleString()} · {result.model_name}</p></div><div className="result-actions"><button className="btn btn--ghost" onClick={()=>window.print()}><Icon name="print" size={16}/>Print result</button><button className="btn btn--primary" onClick={()=>navigate('/app/assessment')}><Icon name="plus" size={16}/>New assessment</button></div></div>

    <section className={`risk-report ${riskClass(result.risk_level)}`}>
      <div className="risk-report__score"><span className="section-kicker">ESTIMATED RISK</span><div className="risk-number">{percent.toFixed(1)}<small>%</small></div><div className="risk-badge">{result.risk_level} risk</div><p>Assessment pattern: <strong>{result.predicted_class === 1 ? 'Higher-risk pattern' : 'Lower-risk pattern'}</strong>.</p></div>
      <div className="risk-spectrum-wrap"><div className="risk-spectrum-labels"><span>Lower risk</span><span>Moderate</span><span>Higher risk</span></div><div className="risk-spectrum"><div className="risk-spectrum__segments"><span/><span/><span/><span/></div><div className="risk-pointer" style={{left:`${Math.min(98,Math.max(2,percent))}%`}}><i/><b>{percent.toFixed(1)}%</b></div></div><div className="risk-spectrum-scale"><span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span></div></div>
      <div className="risk-report__meta"><div><small>Model used</small><strong>{result.model_name}</strong></div><div><small>Decision point</small><strong>{result.threshold}</strong></div><div><small>Classification</small><strong>{result.predicted_class === 1 ? 'Higher-risk pattern' : 'Lower-risk pattern'}</strong></div></div>
    </section>

    <div className="result-grid">
      <section className="panel panel--wide"><div className="panel-head"><div><span className="section-kicker">KEY FACTORS</span><h3>Features influencing this result</h3></div><span className="panel-chip">Top {result.influences?.length || 0}</span></div><div className="influence-list">{result.influences?.map((item)=>{const max=Math.max(...result.influences.map(x=>Math.abs(x.impact)),.01);return <div key={item.feature} className={`influence-row influence-row--${item.direction}`}><div><strong>{item.label}</strong><small>{item.feature} · entered {item.value} · comparison {Number(item.reference).toFixed(1)}</small></div><div className="influence-track"><span style={{width:`${Math.abs(item.impact)/max*100}%`}}/></div><em>{directionLabel[item.direction] || item.direction}</em></div>})}</div></section>
      <section className="panel"><div className="panel-head"><div><span className="section-kicker">ASSESSMENT DETAILS</span><h3>Values used</h3></div></div><div className="submitted-vector">{Object.entries(input).map(([k,v])=><div key={k}><span>{k}</span><strong>{v}</strong></div>)}</div></section>
    </div>
    <div className="safety-banner"><Icon name="shield"/><div><strong>Important</strong><p>{result.disclaimer || 'This estimate is for informational use only and is not a diagnosis. If you have health concerns, speak with a qualified healthcare professional.'}</p></div></div>
  </div>
}
