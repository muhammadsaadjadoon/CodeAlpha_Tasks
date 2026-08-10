import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import Brand from '../components/Brand.jsx'
import { Icon } from '../components/Icons.jsx'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('demo@hearttrack.ai')
  const [password, setPassword] = useState('HeartTrack@2026')
  const [show, setShow] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/app" replace />

  async function submit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(email, password)
      navigate('/app', { replace: true })
    } catch (err) {
      setError(err.message || 'Unable to sign in')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-screen auth-screen--login-v13">
      <div className="auth-noise" />

      <section className="auth-visual auth-login-visual">
        <div className="auth-brand"><Brand /></div>

        <div className="auth-login-hero">
          <div className="auth-kicker">Heart risk assessment workspace</div>
          <h1>A clear, focused way to assess heart risk.</h1>
          <p>
            Enter patient information, review the prediction, and understand the key factors behind the result — all in one focused workspace.
          </p>

          <div className="auth-login-signal" aria-hidden="true">
            <div className="auth-login-signal__head">
              <span><Icon name="pulse" size={17}/> Assessment flow</span>
              <strong>Ready</strong>
            </div>
            <svg viewBox="0 0 760 120" preserveAspectRatio="none">
              <defs>
                <linearGradient id="loginPulse" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#176a83"/>
                  <stop offset="48%" stopColor="#22e6ff"/>
                  <stop offset="100%" stopColor="#19bceb"/>
                </linearGradient>
              </defs>
              <path className="auth-login-signal__shadow" d="M0 68h112l18-2 18-34 22 74 22-45 22 7h112l16-2 18-25 18 53 20-36 20 10h110l18-2 15-18 17 39 20-31 20 10h128"/>
              <path className="auth-login-signal__line" d="M0 68h112l18-2 18-34 22 74 22-45 22 7h112l16-2 18-25 18 53 20-36 20 10h110l18-2 15-18 17 39 20-31 20 10h128"/>
            </svg>
            <div className="auth-login-signal__foot">
              <span>Patient details</span>
              <span>Risk analysis</span>
              <span>Clear result</span>
            </div>
          </div>

          <div className="auth-login-proof">
            <article><span><Icon name="brain" size={19}/></span><div><strong>4 trained models</strong><small>Compared for performance</small></div></article>
            <article><span><Icon name="activity" size={19}/></span><div><strong>13 clinical inputs</strong><small>Guided step by step</small></div></article>
            <article><span><Icon name="database" size={19}/></span><div><strong>920 records</strong><small>UCI heart-disease data</small></div></article>
          </div>
        </div>

        <div className="auth-login-footer">
          <span><Icon name="shield" size={16}/> Your session stays private</span>
          <span>For informational use only · not a medical diagnosis</span>
        </div>
      </section>

      <section className="auth-panel auth-login-panel">
        <div className="auth-panel__inner auth-login-card">
          <div className="auth-mobile-brand"><Brand /></div>

          <div className="auth-heading">
            <span className="auth-step">WELCOME BACK</span>
            <h2>Welcome back</h2>
            <p>Sign in to continue to your workspace.</p>
          </div>

          <form className="auth-form" onSubmit={submit}>
            <label className="field-label">Email address
              <div className="auth-input">
                <span>@</span>
                <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoComplete="email" placeholder="name@example.com" required />
              </div>
            </label>

            <label className="field-label">Password
              <div className="auth-input">
                <Icon name="lock" size={17}/>
                <input value={password} onChange={(e) => setPassword(e.target.value)} type={show ? 'text' : 'password'} autoComplete="current-password" placeholder="Enter your password" required />
                <button type="button" onClick={() => setShow((v) => !v)} aria-label="Toggle password"><Icon name="eye" size={18}/></button>
              </div>
            </label>

            {error && <div className="form-error"><Icon name="info" size={17}/><span>{error}</span></div>}

            <button className="primary-auth-btn" disabled={busy}>
              {busy ? <span className="spinner"/> : <>Sign in <Icon name="arrow" size={18}/></>}
            </button>
          </form>

          <div className="auth-divider"><span>New here?</span></div>
          <Link className="secondary-auth-btn" to="/create-account">Create account <Icon name="chevron" size={17}/></Link>

          <div className="demo-note">
            <span className="demo-note__dot"/>
            <div>
              <strong>Sample account available</strong>
              <small>Use the pre-filled details to sign in, or create your own account.</small>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
