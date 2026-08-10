import { useMemo, useState } from 'react'
import { featureGuide } from '../data/featureGuide.js'
import { Icon } from '../components/Icons.jsx'

const groupIcons = {
  Patient: 'user',
  Symptoms: 'pulse',
  Vitals: 'activity',
  Laboratory: 'database',
  ECG: 'pulse',
  Exercise: 'activity',
  Imaging: 'file',
}

export default function ClinicalGuide() {
  const [query, setQuery] = useState('')
  const [group, setGroup] = useState('All')
  const groups = ['All', ...new Set(featureGuide.map((item) => item.group))]

  const filtered = useMemo(
    () => featureGuide.filter((feature) =>
      (group === 'All' || feature.group === group)
      && `${feature.label} ${feature.key} ${feature.note}`.toLowerCase().includes(query.toLowerCase())
    ),
    [query, group],
  )

  return (
    <div className="page-stack guide-page">
      <div className="guide-toolbar">
        <div className="guide-toolbar__copy">
          <span className="section-kicker">CLINICAL REFERENCE</span>
          <h2>Assessment field guide</h2>
          <p>Use this guide to understand each field, its expected values, and how it is used in the assessment.</p>
        </div>
        <label className="guide-search" aria-label="Search clinical fields">
          <Icon name="book" size={18} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search the guide…" />
        </label>
      </div>

      <div className="filter-tabs" aria-label="Clinical field categories">
        {groups.map((item) => (
          <button className={group === item ? 'active' : ''} onClick={() => setGroup(item)} key={item}>{item}</button>
        ))}
      </div>

      <div className="guide-grid">
        {filtered.map((feature) => {
          const index = featureGuide.indexOf(feature) + 1
          return (
            <article className="guide-card" key={feature.key}>
              <div className="guide-card__index">{String(index).padStart(2, '0')}</div>
              <div className="guide-card__head">
                <span className="guide-card__category">
                  <i><Icon name={groupIcons[feature.group] || 'info'} size={18} /></i>
                  {feature.group}
                </span>
                <code>{feature.key}</code>
              </div>
              <h3>{feature.label}</h3>
              <p>{feature.note}</p>
              <div className="guide-card__foot">
                <div><small>Expected values</small><strong>{feature.range}</strong></div>
                <div><small>Unit</small><strong>{feature.unit || 'category'}</strong></div>
              </div>
            </article>
          )
        })}
      </div>

      <div className="safety-banner">
        <Icon name="book" />
        <div>
          <strong>About this guide</strong>
          <p>These definitions explain the inputs used by HeartTrack. They are for reference only and do not replace professional medical guidance.</p>
        </div>
      </div>
    </div>
  )
}
