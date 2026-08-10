import logo from '../assets-hearttrack-logo.png'

export default function Brand({ compact = false }) {
  return (
    <div className={`brand ${compact ? 'brand--compact' : ''}`}>
      <div className="brand__mark"><img src={logo} alt="" /></div>
      {!compact && <div><div className="brand__name">HeartTrack</div><div className="brand__tagline">Smart Heart Risk Prediction</div></div>}
    </div>
  )
}
