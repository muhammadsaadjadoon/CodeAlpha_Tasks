import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useSession } from '../context/SessionContext.jsx'
import { featureGuide, samplePatient } from '../data/featureGuide.js'
import { Icon } from '../components/Icons.jsx'

const empty = { age:'', sex:'', cp:'', trestbps:'', chol:'', fbs:'', restecg:'', thalach:'', exang:'', oldpeak:'', slope:'', ca:'', thal:'' }
const steps = [
  { id:0, label:'Patient & symptoms', note:'Basic details and chest pain', keys:['age','sex','cp'] },
  { id:1, label:'Vitals & laboratory', note:'Blood pressure, cholesterol, and blood sugar', keys:['trestbps','chol','fbs'] },
  { id:2, label:'ECG & exercise', note:'ECG and exercise response', keys:['restecg','thalach','exang','oldpeak','slope'] },
  { id:3, label:'Imaging & review', note:'Vessel and thallium results', keys:['ca','thal'] },
]

const definitions = {
  age:{label:'Age',type:'number',min:18,max:100,unit:'years',placeholder:'54'},
  sex:{label:'Sex',type:'select',options:[[0,'Female'],[1,'Male']]},
  cp:{label:'Chest pain type',type:'select',options:[[1,'Typical angina'],[2,'Atypical angina'],[3,'Non-anginal pain'],[4,'Asymptomatic']]},
  trestbps:{label:'Resting blood pressure',type:'number',min:70,max:250,unit:'mmHg',placeholder:'130'},
  chol:{label:'Serum cholesterol',type:'number',min:80,max:700,unit:'mg/dL',placeholder:'246'},
  fbs:{label:'Fasting blood sugar > 120 mg/dL',type:'select',options:[[0,'No'],[1,'Yes']]},
  restecg:{label:'Resting ECG result',type:'select',options:[[0,'Normal'],[1,'ST-T abnormality'],[2,'LV hypertrophy']]},
  thalach:{label:'Maximum heart rate achieved',type:'number',min:50,max:250,unit:'bpm',placeholder:'150'},
  exang:{label:'Exercise-induced angina',type:'select',options:[[0,'No'],[1,'Yes']]},
  oldpeak:{label:'ST depression',type:'number',min:-2.5,max:10,step:'0.1',unit:'mm',placeholder:'1.0'},
  slope:{label:'Peak exercise ST slope',type:'select',options:[[1,'Upsloping'],[2,'Flat'],[3,'Downsloping']]},
  ca:{label:'Major vessels',type:'select',options:[[0,'0 vessels'],[1,'1 vessel'],[2,'2 vessels'],[3,'3 vessels']]},
  thal:{label:'Thallium stress-test result',type:'select',options:[[3,'Normal'],[6,'Fixed defect'],[7,'Reversible defect']]},
}

function Field({ name, value, onChange }) {
  const d = definitions[name]
  const guide = featureGuide.find((x)=>x.key===name)
  return <label className="clinical-field"><span className="clinical-field__head"><strong>{d.label}</strong>{d.unit && <em>{d.unit}</em>}</span>{d.type==='select' ? <select value={value} onChange={(e)=>onChange(name,e.target.value)}><option value="">Select an option</option>{d.options.map(([v,l])=><option value={v} key={v}>{l}</option>)}</select> : <div className="number-wrap"><input value={value} onChange={(e)=>onChange(name,e.target.value)} type="number" min={d.min} max={d.max} step={d.step || '1'} placeholder={d.placeholder}/>{d.unit&&<span>{d.unit}</span>}</div>}<small>{guide?.note}</small></label>
}

export default function Assessment() {
  const navigate = useNavigate()
  const { draft, setDraft, recordCase } = useSession()
  const [form, setForm] = useState(draft || empty)
  const [step, setStep] = useState(0)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const completed = useMemo(()=>Object.values(form).filter((v)=>v!=='' && v!==null).length,[form])
  const stepComplete = steps[step].keys.every((k)=>form[k]!=='' && form[k]!==null)
  const allComplete = completed === 13

  function change(name, value) { setForm((x)=>({ ...x,[name]:value })); setError('') }
  function useSample() { const converted=Object.fromEntries(Object.entries(samplePatient).map(([k,v])=>[k,String(v)])); setForm(converted); setDraft(converted); setError('') }
  function reset() { setForm(empty); setDraft(null); setStep(0); setError('') }
  function next() { if (!stepComplete) return setError('Please complete every field in this section before continuing.'); setDraft(form); setStep((s)=>Math.min(3,s+1)); setError('') }
  function back() { setStep((s)=>Math.max(0,s-1)); setError('') }

  async function predict() {
    if (!allComplete) return setError('Please complete all 13 fields before calculating the result.')
    setBusy(true); setError('')
    const payload = Object.fromEntries(Object.entries(form).map(([k,v])=>[k, ['age','sex','cp','fbs','restecg','exang','slope','ca','thal'].includes(k) ? Number.parseInt(v,10) : Number(v)]))
    try {
      const result = await api.predict(payload)
      recordCase(payload,result)
      setDraft(null)
      navigate('/app/assessment/result')
    } catch (err) { setError(err.message || "We couldn't calculate the result. Please try again in a moment.") }
    finally { setBusy(false) }
  }

  return <div className="assessment-page">
    <div className="case-header">
      <div><span className="section-kicker">NEW ASSESSMENT</span><h2>Heart risk assessment</h2><p>Enter the patient details below. Your entries are only kept for this session.</p></div>
      <div className="case-header__actions"><button className="btn btn--ghost" onClick={useSample}>Use example</button><button className="btn btn--quiet" onClick={reset}>Clear form</button></div>
    </div>

    <div className="assessment-progress"><div className="assessment-progress__bar"><span style={{width:`${completed/13*100}%`}}/></div><div><strong>{completed}/13 fields</strong><span>{Math.round(completed/13*100)}% complete</span></div></div>

    <div className="assessment-layout">
      <aside className="assessment-steps">
        <div className="assessment-steps__label">ASSESSMENT STEPS</div>
        {steps.map((s)=>{const done=s.keys.every(k=>form[k]!==''&&form[k]!==null); return <button key={s.id} onClick={()=>setStep(s.id)} className={`${step===s.id?'active':''} ${done?'done':''}`}><span className="step-index">{done?<Icon name="check" size={14}/>:String(s.id+1).padStart(2,'0')}</span><span><strong>{s.label}</strong><small>{s.note}</small></span></button>})}
        <div className="assessment-tip"><Icon name="shield"/><div><strong>Private by default</strong><small>Your entries are cleared when you refresh or leave this session.</small></div></div>
      </aside>

      <section className="assessment-card">
        <div className="assessment-card__head"><div><span>STEP {step+1} OF 4</span><h3>{steps[step].label}</h3><p>{steps[step].note}</p></div><div className="section-count">{steps[step].keys.filter(k=>form[k]!==''&&form[k]!==null).length}<span>/{steps[step].keys.length}</span></div></div>
        <div className={`clinical-grid ${steps[step].keys.length <= 3 ? 'clinical-grid--compact' : ''}`}>{steps[step].keys.map((name)=><Field key={name} name={name} value={form[name]} onChange={change}/>)}</div>
        {step===3 && <div className="review-banner"><Icon name="info"/><div><strong>You're ready to calculate risk when all fields are complete.</strong><p>Review the details, then calculate the estimated heart-risk probability. This result is informational and not a diagnosis.</p></div></div>}
        {error && <div className="form-error form-error--assessment"><Icon name="info" size={17}/><span>{error}</span></div>}
        <div className="assessment-card__footer"><button className="btn btn--quiet" onClick={back} disabled={step===0}>Back</button><span className="footer-help">We'll check each value before calculating the result.</span>{step<3 ? <button className="btn btn--primary" onClick={next}>Continue <Icon name="arrow" size={16}/></button> : <button className="btn btn--primary btn--predict" onClick={predict} disabled={busy||!allComplete}>{busy?<><span className="spinner"/>Calculating…</>:<>Calculate risk <Icon name="pulse" size={17}/></>}</button>}</div>
      </section>

      <aside className="case-inspector">
        <div className="case-inspector__head"><span>CURRENT INPUTS</span><strong>{completed === 13 ? 'Ready' : 'In progress'}</strong></div>
        <div className="vector-list">{featureGuide.map((f)=><div key={f.key} className={form[f.key]!==''?'filled':''}><span>{f.key}</span><strong>{form[f.key]!==''?form[f.key]:'—'}</strong><small>{f.unit}</small></div>)}</div>
        <div className="vector-footer"><span>Completed</span><strong>{Math.round(completed/13*100)}%</strong><div><span style={{width:`${completed/13*100}%`}}/></div></div>
      </aside>
    </div>
  </div>
}
