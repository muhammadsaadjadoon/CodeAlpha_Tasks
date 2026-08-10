import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext.jsx'
import { Icon } from '../components/Icons.jsx'

export default function Cases() {
  const { cases, clearCases } = useSession()
  const navigate = useNavigate()
  function exportCsv() {
    if (!cases.length) return
    const rows = [['case_id','created_at','probability','risk_level','model','predicted_class'], ...cases.map(c=>[c.id,c.createdAt,c.result.probability,c.result.risk_level,c.result.model_name,c.result.predicted_class])]
    const csv = rows.map(r=>r.map(v=>`"${String(v).replaceAll('"','""')}"`).join(',')).join('\n')
    const url = URL.createObjectURL(new Blob([csv],{type:'text/csv'})); const a=document.createElement('a'); a.href=url; a.download='hearttrack-session-cases.csv'; a.click(); URL.revokeObjectURL(url)
  }
  return <div className="page-stack"><div className="page-action-row"><div><span className="section-kicker">THIS SESSION</span><h2>{cases.length} assessment{cases.length===1?'':'s'}</h2><p>These assessments are available only for this session and are cleared when you refresh the page.</p></div><div><button className="btn btn--ghost" onClick={exportCsv} disabled={!cases.length}><Icon name="download" size={16}/>Download CSV</button><button className="btn btn--primary" onClick={()=>navigate('/app/assessment')}><Icon name="plus" size={16}/>New assessment</button></div></div>
  {cases.length ? <section className="panel table-panel"><div className="case-table"><div className="case-table__head"><span>Assessment</span><span>Time</span><span>Risk estimate</span><span>Risk level</span><span>Result</span><span>Model</span></div>{cases.map(c=><div className="case-table__row" key={c.id}><strong>{c.id}</strong><span>{new Date(c.createdAt).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</span><span className="mono">{Number(c.result.percent ?? c.result.probability*100).toFixed(1)}%</span><span><b className={`mini-risk mini-risk--${c.result.risk_level.toLowerCase().replace(' ','-')}`}>{c.result.risk_level}</b></span><span>{c.result.predicted_class===1?'Higher-risk pattern':'Lower-risk pattern'}</span><span>{c.result.model_name}</span></div>)}</div><div className="table-footer"><span>Current session</span><button className="danger-text" onClick={clearCases}>Clear all</button></div></section> : <section className="empty-panel"><div className="empty-icon"><Icon name="users" size={28}/></div><h3>No assessments yet</h3><p>Complete an assessment and it will appear here until the page is refreshed.</p><button className="btn btn--primary" onClick={()=>navigate('/app/assessment')}>Start assessment</button></section>}</div>
}
