import { useEffect, useMemo, useState } from 'react'
import { api } from '../api/client.js'
import { featureGuide } from '../data/featureGuide.js'
import { Icon } from '../components/Icons.jsx'

export default function DatasetLab() {
  const [data,setData]=useState(null); const [error,setError]=useState('')
  useEffect(()=>{api.datasetReport().then(setData).catch(e=>setError(e.message))},[])
  const missing=useMemo(()=>data?.missing_values?Object.entries(data.missing_values).sort((a,b)=>b[1]-a[1]):[],[data])
  if(error) return <div className="empty-panel"><h3>Training data details unavailable</h3><p>{error}</p></div>
  return <div className="page-stack">
    <section className="dataset-hero"><div><span className="section-kicker">TRAINING DATA</span><h2>{data?.dataset_name || 'UCI Heart Disease cohorts'}</h2><p>Heart-disease records used to train and evaluate the models. The source location is kept for analysis and is not used to calculate risk.</p></div><div className="dataset-hero__stats"><div><strong>{data?.rows||'—'}</strong><span>records</span></div><div><strong>{data?.features||13}</strong><span>model inputs</span></div><div><strong>{data?`${(data.positive_rate*100).toFixed(1)}%`:'—'}</strong><span>heart disease present</span></div></div></section>
    <div className="dataset-grid"><section className="panel panel--wide"><div className="panel-head"><div><span className="section-kicker">DATA SOURCES</span><h3>Records by source</h3></div></div><div className="cohort-cards">{data?.source_counts&&Object.entries(data.source_counts).map(([name,count])=><article key={name}><div className="cohort-card__top"><span>{name}</span><strong>{count}</strong></div><div className="cohort-card__bar"><span style={{width:`${count/data.rows*100}%`}}/></div><small>{(count/data.rows*100).toFixed(1)}% of all records</small></article>)}</div></section>
    <section className="panel"><div className="panel-head"><div><span className="section-kicker">DATA QUALITY</span><h3>Missing values</h3></div></div><div className="missing-list">{missing.map(([key,count])=><div key={key}><div><span>{key}</span><strong>{count}</strong></div><div><span style={{width:`${Math.min(100,(count/(data?.rows||920))*100)}%`}}/></div></div>)}</div></section>
    <section className="panel"><div className="panel-head"><div><span className="section-kicker">MODEL INPUTS</span><h3>13 clinical features</h3></div></div><div className="feature-cloud">{featureGuide.map(f=><span key={f.key}><b>{f.key}</b>{f.group}</span>)}</div></section></div>
    <section className="panel"><div className="panel-head"><div><span className="section-kicker">ABOUT THE DATA</span><h3>Dataset notes</h3></div></div><div className="note-grid">{data?.notes?.map((note,i)=><div key={i}><span>{String(i+1).padStart(2,'0')}</span><p>{note}</p></div>)}</div></section>
    <div className="safety-banner"><Icon name="database"/><div><strong>Keep the data in context</strong><p>These historical records are useful for model development but may not reflect today's populations or clinical practice.</p></div></div>
  </div>
}
