import React, {useEffect, useMemo, useState} from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, BarChart3, Brain, CheckCircle2, ChevronRight, Database, FileDown, Gauge, History, LayoutDashboard, Lock, LogOut, Menu, Search, Settings, ShieldCheck, Sparkles, Upload, UserRound, Users, Workflow } from 'lucide-react';
import { api, downloadUrl } from './api';
import './styles.css';
import logo from './assets/credora-logo.png';

const nav = [
  ['overview','Overview',LayoutDashboard], ['scoring','Live Scoring',Gauge], ['models','Model Analytics',Brain], ['insights','Insights',Sparkles], ['workflow','Workflow',Workflow], ['applicants','Applicants',Users], ['history','Assessment History',History], ['settings','Settings',Settings]
];

function fmt(n, suffix='') { if (n === null || n === undefined || Number.isNaN(Number(n))) return '—'; return Number(n).toLocaleString()+suffix; }
function pct(n) { return n === null || n === undefined ? '—' : `${Math.round(Number(n)*100)}%`; }
function todayDate(v) { return v ? new Date(v).toLocaleDateString() : '—'; }
function useHashRoute(defaultRoute='overview') {
  const get = () => (location.hash || `#${defaultRoute}`).slice(1);
  const [route, setRoute] = useState(get);
  useEffect(() => { const on = () => setRoute(get()); window.addEventListener('hashchange', on); if(!location.hash) location.hash=defaultRoute; return () => window.removeEventListener('hashchange', on); }, []);
  const go = (r) => { location.hash = r; setRoute(r); };
  return [route, go];
}
function Toast({toast}) { return toast ? <div className={`toast ${toast.type||''}`}>{toast.text}</div> : null; }
function Empty({title='No records yet', body='Run your first credit assessment to populate this section.'}){ return <div className="empty"><Sparkles size={22}/><b>{title}</b><span>{body}</span></div>; }
function Loader(){ return <div className="skeleton-grid"><div/><div/><div/></div>; }
function Stat({label,value,sub,icon:Icon=Activity}){ return <div className="stat-card"><div><span>{label}</span><b>{value}</b><small>{sub}</small></div><Icon size={24}/></div>; }
function Bars({data}) { const max=Math.max(1,...(data||[]).map(d=>d.value||d.count||0)); return <div className="bars">{(data||[]).map((d,i)=><div className="bar-row" key={i}><span>{d.name||d.date}</span><div><i style={{width:`${((d.value??d.count??0)/max)*100}%`}}/></div><b>{d.value??d.count??0}</b></div>)}</div> }
function Curve({data,x='fpr',y='tpr'}) { const pts=(data||[]).map((d,i)=>`${10+(Number(d[x]||0)*180)},${190-(Number(d[y]||0)*180)}`).join(' '); return <svg className="curve" viewBox="0 0 220 220"><path d="M10 190 L210 10" stroke="rgba(255,255,255,.12)"/><polyline fill="none" stroke="var(--gold)" strokeWidth="4" points={pts}/><text x="10" y="215">0</text><text x="188" y="215">1</text></svg> }

const initialScore = {
  full_name:'', email:'', phone:'', age:35, gender:'not_specified', employment_status:'employed', employment_duration:4,
  annual_income:65000, monthly_income:5400, existing_debt:12000, monthly_expenses:3200, savings:9000,
  loan_amount:18000, loan_purpose:'personal', loan_term:36, existing_loans:2,
  credit_history_length:6, previous_defaults:0, late_payments:0, payment_behaviour:'consistent', credit_utilization:.32, outstanding_credit_balance:8000
};
function fieldLabel(k){ return k.replaceAll('_',' ').replace(/\b\w/g, m=>m.toUpperCase()); }
function Input({form,setForm,name,type='text',required=false}){ return <label className="field"><span>{fieldLabel(name)} {required && <em>*</em>}</span><input type={type} value={form[name]??''} onChange={e=>setForm({...form,[name]: type==='number'? Number(e.target.value): e.target.value})} required={required}/></label> }
function Select({form,setForm,name,options}){ return <label className="field"><span>{fieldLabel(name)}</span><select value={form[name]??''} onChange={e=>setForm({...form,[name]:e.target.value})}>{options.map(o=><option key={o} value={o}>{fieldLabel(o)}</option>)}</select></label> }

function Auth({onAuth}){
  const [mode,setMode]=useState('login');
  const [open,setOpen]=useState(false);
  const [form,setForm]=useState({full_name:'',email:'',password:''});
  const [error,setError]=useState('');
  const openAuth=(next)=>{setMode(next);setError('');setForm({full_name:'',email:'',password:''});setOpen(true)};
  const switchMode=()=>{setMode(mode==='login'?'register':'login');setError('')};
  const submit=async(e)=>{ e.preventDefault(); setError(''); try{ const data=await api(`/api/auth/${mode==='login'?'login':'register'}`,{method:'POST',body:JSON.stringify(form)}); onAuth(data.user); }catch(err){ setError(err.message); } };
  return <main className="auth-page single-auth">
    <section className="auth-panel left auth-hero-only">
      <div className="auth-hero-top">
        <div className="auth-brand-lockup"><img src={logo}/><div><strong>Credora</strong><span>Risk Intelligence</span></div></div>
        <div className="auth-actions"><button className="link" onClick={()=>openAuth('login')}>Sign in</button><button className="primary" onClick={()=>openAuth('register')}>Create account</button></div>
      </div>
      <div className="auth-hero-body">
        <div className="auth-copy"><p className="kicker">Credora Platform</p><h1>AI-powered credit assessment for serious financial decisions.</h1><p>Train models, analyze applicants, track performance, and keep every assessment in a secure workspace.</p></div>
        <div className="auth-side-card"><Sparkles size={22}/><b>Production-ready risk workspace</b><span>Secure sign-in, backend-saved records, real model evaluation, and assessment history in one enterprise dashboard.</span></div>
      </div>
      <div className="security-list"><span><ShieldCheck/> Secure account access</span><span><Database/> Backend-saved records</span><span><Brain/> Real model evaluation</span></div>
    </section>
    {open&&<div className="auth-modal-backdrop" onClick={()=>setOpen(false)}><section className="auth-panel auth-modal" onClick={e=>e.stopPropagation()}><button className="modal-close" onClick={()=>setOpen(false)} aria-label="Close">×</button><p className="kicker">Account Access</p><h2>{mode==='login'?'Sign in':'Create account'}</h2><form onSubmit={submit}>{mode==='register'&&<input placeholder="Full name" value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/>}<input placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/><input placeholder="Password" type="password" autoComplete={mode==='login'?'current-password':'new-password'} value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/>{error&&<p className="error">{error}</p>}<button className="primary wide">{mode==='login'?'Sign in':'Create secure account'}</button></form><button className="link modal-switch" onClick={switchMode}>{mode==='login'?'Create a new account':'Already have an account?'}</button></section></div>}
  </main>
}

function SidebarProfile({user}){
  return <div className="sidebar-profile"><img src={user.profile_image?downloadUrl(user.profile_image):logo}/><div><b>{user.full_name||'User Profile'}</b><span>{user.email||'Workspace account'}</span><small>Active workspace</small></div></div>
}

function Shell({user,setUser}){
  const [route,go]=useHashRoute(); const [toast,setToast]=useState(null); const [open,setOpen]=useState(false);
  const notify=(text,type='')=>{setToast({text,type}); setTimeout(()=>setToast(null),2800)};
  const logout=async()=>{ await api('/api/auth/logout',{method:'POST'}); setUser(null); };
  const Current = {overview:Overview,scoring:Scoring,models:Models,insights:Insights,workflow:WorkflowPage,applicants:Applicants,history:HistoryPage,settings:SettingsPage}[route] || Overview;
  return <div className="app-shell"><aside className={`sidebar ${open?'open':''}`}><div className="brand"><img src={logo}/><div><strong>Credora</strong><span>Risk Intelligence</span></div></div><p className="nav-title">Command Center</p>{nav.map(([id,label,Icon])=><button key={id} className={route===id?'active':''} onClick={()=>{go(id);setOpen(false)}}><Icon size={20}/>{label}</button>)}<SidebarProfile user={user}/></aside><main className="workspace"><header className="topbar"><button className="menu" onClick={()=>setOpen(true)}><Menu/></button><div><p>Credora Platform</p><h2>{nav.find(n=>n[0]===route)?.[1]||'Overview'}</h2></div><div className="user-chip"><span>{user.full_name}</span><button onClick={logout}><LogOut size={16}/>Logout</button></div></header><Current go={go} notify={notify} user={user} setUser={setUser}/></main><Toast toast={toast}/></div>
}

function Overview({go}){ const [data,setData]=useState(null); const [err,setErr]=useState(''); useEffect(()=>{Promise.all([api('/api/dashboard/summary'),api('/api/dashboard/risk-distribution'),api('/api/dashboard/score-distribution'),api('/api/dashboard/assessment-trend'),api('/api/dashboard/recent-assessments')]).then(([summary,risk,score,trend,recent])=>setData({summary,risk,score,trend,recent})).catch(e=>setErr(e.message))},[]); if(err)return <p className="error page-pad">{err}</p>; if(!data)return <Loader/>; return <section className="page"><div className="hero-card"><div><p className="kicker">Operational Dashboard</p><h1>Credit risk command center.</h1><p>Every number below comes from saved applicant assessments and active model results.</p></div><button onClick={()=>go('scoring')} className="primary">New Assessment <ChevronRight/></button></div><div className="stats"><Stat label="Total Assessments" value={fmt(data.summary.total_assessments)} icon={History}/><Stat label="Creditworthy Applicants" value={fmt(data.summary.creditworthy_applicants)} icon={CheckCircle2}/><Stat label="High-Risk Applicants" value={fmt(data.summary.high_risk_applicants)} icon={ShieldCheck}/><Stat label="Average Credit Score" value={fmt(data.summary.average_credit_score)} icon={Gauge}/></div><div className="grid three dashboard-chart-grid"><Panel title="Risk Distribution"><Bars data={data.risk}/></Panel><Panel title="Credit Score Distribution"><Bars data={data.score}/></Panel><Panel title="Weekly Assessment Trend"><Bars data={data.trend.map(x=>({name:new Date(x.date).toLocaleDateString(undefined,{weekday:'short'}),value:x.count}))}/></Panel></div><Panel title="Recent Assessments" action={<button onClick={()=>go('history')}>View History</button>}>{data.recent.items.length?<Table rows={data.recent.items} cols={['applicant','credit_score','risk_level','recommendation','created_at']} />:<Empty/>}</Panel></section> }
function Panel({title,children,action}){ return <div className="panel"><div className="panel-head"><h3>{title}</h3>{action}</div>{children}</div> }
function Table({rows,cols,onView,onDelete}){ return <div className="table-wrap"><table><thead><tr>{cols.map(c=><th key={c}>{fieldLabel(c)}</th>)}{(onView||onDelete)&&<th>Actions</th>}</tr></thead><tbody>{rows.map((r,i)=><tr key={r.id||i}>{cols.map(c=><td key={c}>{c.includes('date')||c==='created_at'?todayDate(r[c]):String(r[c]??'—')}</td>)}{(onView||onDelete)&&<td className="actions">{onView&&<button onClick={()=>onView(r)}>View</button>}{onDelete&&<button className="danger" onClick={()=>onDelete(r)}>Delete</button>}</td>}</tr>)}</tbody></table></div> }

function Scoring({notify}){
  const [form,setForm]=useState(initialScore);
  const [result,setResult]=useState(null);
  const [busy,setBusy]=useState(false);
  const submit=async(e)=>{
    e.preventDefault();
    setBusy(true);
    try{
      const r=await api('/api/scoring/predict-and-save',{method:'POST',body:JSON.stringify(form)});
      setResult(r);
      notify('Assessment completed and saved.','good');
      requestAnimationFrame(()=>document.getElementById('prediction-result')?.scrollIntoView({behavior:'smooth',block:'start'}));
    }catch(err){notify(err.message,'bad')}finally{setBusy(false)}
  };
  const groups=[
    ['Applicant Information',['full_name','email','phone','age'],['gender',['not_specified','female','male'], 'employment_status',['employed','self_employed','contract','student','unemployed','retired']]],
    ['Financial Information',['employment_duration','annual_income','monthly_income','existing_debt','monthly_expenses','savings']],
    ['Loan Information',['loan_amount','loan_term','existing_loans'],['loan_purpose',['personal','debt_consolidation','home','auto','business','education','medical']]],
    ['Credit Information',['credit_history_length','previous_defaults','late_payments','credit_utilization','outstanding_credit_balance'],['payment_behaviour',['consistent','minor_delays','irregular','poor']]]
  ];
  return <section className="page scoring-page">
    <form className="panel form-panel scoring-form" onSubmit={submit}>
      <p className="kicker">Live Scoring</p>
      <div className="form-title-row"><div><h1>Analyze creditworthiness</h1><p>Enter applicant, financial, loan and credit details. The active backend model will calculate the score and risk profile.</p></div></div>
      {groups.map((g)=><div className="form-section" key={g[0]}><h3>{g[0]}</h3><div className="form-grid spacious">{g[1].map(n=><Input key={n} form={form} setForm={setForm} name={n} type={['full_name','email','phone'].includes(n)?'text':'number'} required={['full_name','email'].includes(n)}/>) }{g[2]&&<Select form={form} setForm={setForm} name={g[2][0]} options={g[2][1]}/>} {g[2]&&g[2][2]&&<Select form={form} setForm={setForm} name={g[2][2]} options={g[2][3]}/>}</div></div>)}
      <button className="primary wide analyze-btn" disabled={busy}>{busy?'Analyzing applicant profile...':'Analyze Creditworthiness'}</button>
    </form>
    {result && <PredictionCard result={result} setResult={setResult} setForm={setForm}/>}  
  </section>
}
function RiskMeter({score}){
  const pctScore=Math.max(0,Math.min(100,((Number(score||300)-300)/550)*100));
  return <div className="risk-meter"><div className="risk-track"><i style={{width:`${pctScore}%`}}/></div><div className="risk-scale"><span>High</span><span>Elevated</span><span>Moderate</span><span>Low</span></div></div>
}
function PredictionCard({result,setResult,setForm}){
  return <div id="prediction-result" className="panel prediction-card">
    <div className="prediction-head"><div><p className="kicker">Prediction Result</p><h2>Enterprise credit assessment</h2><p>Generated from the active production model and saved through the backend when auto-save is enabled.</p></div><div className="score-badge"><b>{result.credit_score}</b><span>{result.risk_level}</span></div></div>
    <RiskMeter score={result.credit_score}/>
    <div className="prediction-metrics">
      <span><small>Credit Score</small><b>{result.credit_score}</b></span>
      <span><small>Risk Level</small><b>{result.risk_level}</b></span>
      <span><small>Probability</small><b>{pct(result.probability)}</b></span>
      <span><small>Recommendation</small><b>{result.recommendation}</b></span>
      <span><small>Confidence</small><b>{pct(result.confidence)}</b></span>
      <span><small>Active Model</small><b>{result.model_name}</b></span>
      <span><small>Model Version</small><b>{result.model_version}</b></span>
    </div>
    <div className="factor-grid">
      <FactorList title="Positive Factors" items={result.positive_factors}/>
      <FactorList title="Key Risk Factors" items={result.risk_factors}/>
      <FactorList title="Improvement Suggestions" items={result.improvement_recommendations}/>
    </div>
    <div className="row result-actions">
      {result.assessment_id && <button onClick={()=>window.open(downloadUrl(`/api/assessments/${result.assessment_id}/report`),'_blank')}>Download Report</button>}
      {result.assessment_id && <button onClick={()=>window.open(downloadUrl(`/api/assessments/${result.assessment_id}/report`),'_blank')}>View Full Record</button>}
      <button onClick={()=>{setForm(initialScore);setResult(null);window.scrollTo({top:0,behavior:'smooth'})}}>Start New Assessment</button>
    </div>
  </div>
}
function FactorList({title,items}){ return <div className="factors"><h4>{title}</h4>{(items||[]).length?(items||[]).map((x,i)=><p key={i}>• {x}</p>):<p>No factor signal returned.</p>}</div> }
function ModelSelector({value,onChange,items}){ return <label className="model-select"><span>Model</span><select value={value} onChange={onChange}>{items.map(x=><option key={x.model_name}>{x.model_name}</option>)}</select></label> }
function FactorInsightList({title,items,type}){ return <div className="factor-insight-list"><h4>{title}</h4>{(items||[]).length?(items||[]).map((x,i)=><div className={`factor-insight ${type}`} key={x.feature||i}><div><b>{x.display_name||fieldLabel(x.feature||'Factor')}</b><span>{x.feature}</span></div><strong>{Math.round(Number(x.percentage ?? x.importance ?? 0))}%</strong></div>):<Empty title="No model factors yet" body="Train the models to generate feature importance signals."/>}</div> }
function Models(){
  const [data,setData]=useState(null);
  const [sel,setSel]=useState('');
  useEffect(()=>{api('/api/models').then(d=>{setData(d.items);setSel(d.items?.[0]?.model_name||'')})},[]);
  if(!data)return <Loader/>;
  const m=data.find(x=>x.model_name===sel)||data[0];
  return <section className="page">
    <div className="section-title model-title"><div><p className="kicker">Model Analytics</p><h1>Validated production intelligence.</h1></div><ModelSelector value={sel} onChange={e=>setSel(e.target.value)} items={data}/></div>
    <div className="stats model-stats"><Stat label="Accuracy" value={pct(m.accuracy)}/><Stat label="Precision" value={pct(m.precision)}/><Stat label="Recall" value={pct(m.recall)}/><Stat label="F1 Score" value={pct(m.f1_score)}/><Stat label="ROC-AUC" value={pct(m.roc_auc)}/></div>
    <div className="grid two"><Panel title="Confusion Matrix"><div className="matrix">{Object.entries(m.confusion_matrix).map(([k,v])=><div key={k}><span>{fieldLabel(k)}</span><b>{v}</b></div>)}</div></Panel><Panel title="ROC Curve"><Curve data={m.roc_curve_data}/></Panel><Panel title="Precision-Recall Curve"><Curve data={m.precision_recall_curve_data} x="recall" y="precision"/></Panel><Panel title="Feature Importance"><Bars data={m.feature_importance.map(x=>({name:x.feature,value:Math.round(x.importance*1000)}))}/></Panel></div>
    <Panel title="Model Comparison"><Table rows={data.map(x=>({...x,status:x.is_active?'Production':'Available'}))} cols={['model_name','accuracy','precision','recall','f1_score','roc_auc','status']}/></Panel>
  </section>
}

function DatasetQuality({summary}){
  const cleanRecords = summary.clean_records ?? Math.max(0, Number(summary.total_records || 0) - Number(summary.duplicate_rows || 0));
  const items = [
    ['Clean Records', cleanRecords],
    ['Validated Features', summary.total_features],
    ['Missing Values', summary.missing_values],
    ['Duplicate Rows', summary.duplicate_rows]
  ];
  return <div className="quality-list">{items.map(([label,value])=><div key={label} className="quality-row"><span>{label}</span><b>{fmt(value)}</b></div>)}</div>
}
function Insights(){
  const [data,setData]=useState(null);
  useEffect(()=>{Promise.all([api('/api/insights/summary'),api('/api/insights/income-distribution'),api('/api/insights/debt-distribution'),api('/api/insights/loan-distribution'),api('/api/insights/age-distribution'),api('/api/insights/employment-distribution')]).then(([summary,income,debt,loan,age,employment])=>setData({summary,income,debt,loan,age,employment}))},[]);
  if(!data)return <Loader/>;
  return <section className="page">
    <div className="stats"><Stat label="Total Records" value={fmt(data.summary.total_records)}/><Stat label="Features" value={fmt(data.summary.total_features)}/><Stat label="Missing Values" value={fmt(data.summary.missing_values)}/><Stat label="Duplicates" value={fmt(data.summary.duplicate_rows)}/></div>
    <div className="grid three insights-grid"><Panel title="Income Distribution"><Bars data={data.income}/></Panel><Panel title="Debt Distribution"><Bars data={data.debt}/></Panel><Panel title="Loan Distribution"><Bars data={data.loan}/></Panel><Panel title="Age Distribution"><Bars data={data.age}/></Panel><Panel title="Employment Status"><Bars data={data.employment}/></Panel><Panel title="Dataset Quality"><DatasetQuality summary={data.summary}/></Panel></div>
  </section>
}
function WorkflowPage(){ const [data,setData]=useState(null); useEffect(()=>{api('/api/workflow/status').then(setData)},[]); if(!data)return <Loader/>; return <section className="page workflow-page"><div className="section-title workflow-title"><p className="kicker">ML Workflow</p><h1>End-to-end system status.</h1></div><div className="workflow-list">{data.steps.map((s,i)=><div className="workflow-item" key={s.name}><span>{String(i+1).padStart(2,'0')}</span><div><b>{s.name}</b><p>{s.description}</p><small>{s.status} · {s.validation_status}</small></div></div>)}</div><div className="stats"><Stat label="Frontend" value={data.deployment.frontend}/><Stat label="Backend" value={data.deployment.backend}/><Stat label="Database" value={data.deployment.database}/><Stat label="Model" value={data.deployment.model}/></div></section> }
function Applicants({notify}){
  const [rows,setRows]=useState([]),[q,setQ]=useState(''),[risk,setRisk]=useState(''),[sort,setSort]=useState('latest');
  const load=()=>api(`/api/applicants?q=${encodeURIComponent(q)}&risk=${encodeURIComponent(risk)}&sort=${encodeURIComponent(sort)}&page_size=5000`).then(d=>setRows(d.items));
  useEffect(()=>{load()},[]);
  const reset=()=>{setQ('');setRisk('');setSort('latest');api('/api/applicants?sort=latest&page_size=5000').then(d=>setRows(d.items));};
  const del=async(r)=>{if(confirm('Delete this applicant and related assessments?')){await api(`/api/applicants/${r.id}`,{method:'DELETE'});notify('Applicant deleted.');load()}};
  return <section className="page"><Toolbar title="Applicants" q={q} setQ={setQ} load={load} risk={risk} setRisk={setRisk} sort={sort} setSort={setSort} onReset={reset} filters="applicants"/><Panel title="Applicant Records">{rows.length?<Table rows={rows} cols={['full_name','phone','email','annual_income','latest_credit_score','current_risk_level','last_assessment']} onDelete={del}/>:<Empty title="No applicants yet"/>}</Panel></section>
}
function HistoryPage({notify}){ const [rows,setRows]=useState([]),[q,setQ]=useState(''); const load=()=>api(`/api/assessments?q=${encodeURIComponent(q)}&page_size=5000`).then(d=>setRows(d.items)); useEffect(()=>{load()},[]); const del=async(r)=>{if(confirm('Delete this assessment?')){await api(`/api/assessments/${r.id}`,{method:'DELETE'});notify('Assessment deleted.');load()}}; return <section className="page"><Toolbar title="Assessment History" q={q} setQ={setQ} load={load} action={<a className="primary small" href={downloadUrl('/api/assessments/export/csv')}>Export CSV</a>}/><Panel title="Saved Assessments">{rows.length?<Table rows={rows} cols={['assessment_reference','applicant','created_at','credit_score','risk_level','recommendation','probability','model_name']} onView={(r)=>window.open(downloadUrl(`/api/assessments/${r.id}/report`),'_blank')} onDelete={del}/>:<Empty title="No assessments available yet"/>}</Panel></section> }
function Toolbar({title,q,setQ,load,action,risk,setRisk,sort,setSort,onReset,filters}){
  const hasFilters=Boolean(q||risk||(sort&&sort!=='latest'));
  return <div className="toolbar enhanced-toolbar"><div><p className="kicker">Records</p><h1>{title}</h1></div><div className="search toolbar-controls"><label className="search-box"><Search size={18}/><input placeholder="Search by name, email or phone" value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>e.key==='Enter'&&load()}/></label>{filters==='applicants'&&<><select className="control-select" value={risk} onChange={e=>setRisk(e.target.value)}><option value="">All risk levels</option><option>Low Risk</option><option>Moderate Risk</option><option>Elevated Risk</option><option>High Risk</option></select><select className="control-select" value={sort} onChange={e=>setSort(e.target.value)}><option value="latest">Latest assessment</option><option value="score_desc">Highest score</option><option value="score_asc">Lowest score</option></select></>}<button className="filter-btn" onClick={load}>Filter</button>{hasFilters&&onReset&&<button className="reset-btn" onClick={onReset}>Reset</button>}{action}</div></div>
}
function Toggle({form,setForm,name,label}){return <label className="toggle-row"><span>{label}</span><input type="checkbox" checked={Boolean(form[name])} onChange={e=>setForm({...form,[name]:e.target.checked})}/><i/></label>}
function SettingsPage({user,setUser,notify}){
  const [form,setForm]=useState(user);
  const [models,setModels]=useState([]);
  const [pass,setPass]=useState({current_password:'',new_password:'',confirm_password:''});
  useEffect(()=>{api('/api/settings').then(d=>{setForm(d.settings);setModels(d.available_models||[])}).catch(()=>{})},[]);
  const save=async()=>{try{const d=await api('/api/settings',{method:'PUT',body:JSON.stringify(form)});setUser(d.user);setForm(d.user);notify('Settings saved.','good')}catch(e){notify(e.message,'bad')}};
  const change=async()=>{if(pass.new_password!==pass.confirm_password){notify('New password and confirmation do not match.','bad');return}try{await api('/api/settings/change-password',{method:'POST',body:JSON.stringify({current_password:pass.current_password,new_password:pass.new_password})});setPass({current_password:'',new_password:'',confirm_password:''});notify('Password updated.','good')}catch(e){notify(e.message,'bad')}};
  const upload=async(e)=>{const file=e.target.files?.[0]; if(!file)return; const fd=new FormData(); fd.append('file',file); try{const d=await api('/api/auth/profile-image',{method:'POST',body:fd}); setUser(d.user); setForm(d.user); notify('Profile image updated.','good')}catch(err){notify(err.message,'bad')}};
  const defaultModelOptions=[''].concat(models.map(m=>m.name));
  return <section className="page settings-grid settings-page">
    <Panel title="Account"><div className="profile-card refined"><img src={user.profile_image?downloadUrl(user.profile_image):logo}/><h2>{user.full_name}</h2><p>{user.email}</p><label className="upload-btn"><Upload size={16}/> Upload profile image<input type="file" accept="image/*" onChange={upload}/></label></div><div className="settings-form"><Input form={form} setForm={setForm} name="full_name"/><Input form={form} setForm={setForm} name="email"/><button className="primary wide" onClick={save}>Save Changes</button></div></Panel>
    <Panel title="Application"><div className="settings-form"><Select form={form} setForm={setForm} name="theme" options={['dark','light','system']}/><Select form={form} setForm={setForm} name="preferred_language" options={['English']}/><label className="field"><span>Default ML Model</span><select value={form.default_model||''} onChange={e=>setForm({...form,default_model:e.target.value||null})}>{defaultModelOptions.map(v=><option key={v} value={v}>{v||'Active Production Model'}</option>)}</select></label><Input form={form} setForm={setForm} name="prediction_threshold" type="number"/><Toggle form={form} setForm={setForm} name="auto_save" label="Auto Save Assessments"/><Toggle form={form} setForm={setForm} name="assessment_alerts" label="Assessment Alerts"/><button className="primary wide" onClick={save}>Save Preferences</button></div></Panel>
    <Panel title="Security"><div className="settings-form security-form"><label className="field"><span>Current Password</span><input type="password" autoComplete="current-password" value={pass.current_password} onChange={e=>setPass({...pass,current_password:e.target.value})}/></label><label className="field"><span>New Password</span><input type="password" autoComplete="new-password" value={pass.new_password} onChange={e=>setPass({...pass,new_password:e.target.value})}/></label><label className="field"><span>Confirm New Password</span><input type="password" autoComplete="new-password" value={pass.confirm_password} onChange={e=>setPass({...pass,confirm_password:e.target.value})}/></label><button className="primary wide" onClick={change}>Change Password</button></div></Panel>
  </section>
}

function useCredoraTheme(theme){
  useEffect(()=>{
    const choose=()=> theme==='system' ? (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark') : (theme||'dark');
    const apply=()=>document.documentElement.setAttribute('data-theme', choose());
    apply();
    if(theme==='system'){
      const media=window.matchMedia('(prefers-color-scheme: light)');
      media.addEventListener?.('change', apply);
      return ()=>media.removeEventListener?.('change', apply);
    }
  },[theme]);
}

function App(){ const [user,setUser]=useState(null); const [loading,setLoading]=useState(true); useCredoraTheme(user?.theme||'dark'); useEffect(()=>{api('/api/auth/me').then(d=>setUser(d.user)).catch(()=>{}).finally(()=>setLoading(false))},[]); if(loading)return <Loader/>; return user?<Shell user={user} setUser={setUser}/>:<Auth onAuth={setUser}/> }
createRoot(document.getElementById('root')).render(<App/>);
