import { useMemo, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import Brand from '../components/Brand.jsx'
import { Icon } from '../components/Icons.jsx'

export default function Register() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm: '' })
  const [show, setShow] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const strength = useMemo(() => {
    const p = form.password
    return [p.length >= 10, /[A-Z]/.test(p), /[a-z]/.test(p), /\d/.test(p)].filter(Boolean).length
  }, [form.password])

  if (user) return <Navigate to="/app" replace />
  const set = (key) => (e) => setForm((prev) => ({ ...prev, [key]: e.target.value }))

  async function submit(event) {
    event.preventDefault()
    setError('')
    if (form.password !== form.confirm) return setError('Passwords do not match.')
    if (strength < 4) return setError('Use at least 10 characters with upper, lower and numeric characters.')
    setBusy(true)
    try {
      await register(form.full_name, form.email, form.password)
      navigate('/app', { replace: true })
    } catch (err) {
      setError(err.message || 'Could not create account')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-screen auth-screen--register-v14">
      <div className="auth-noise" />

      <section className="auth-visual auth-register-visual">
        <div className="auth-brand"><Brand /></div>

        <div className="auth-register-hero">
          <div className="auth-kicker">GET STARTED</div>
          <h1>Set up your workspace in a few seconds.</h1>
          <p>
            Create an account to start assessments, review results, and manage your profile in one place.
          </p>

          <div className="auth-register-grid">
            <article>
              <span><Icon name="shield" size={19}/></span>
              <div><strong>Private by default</strong><small>Your activity stays within your current session</small></div>
            </article>
            <article>
              <span><Icon name="lock" size={19}/></span>
              <div><strong>Password protection</strong><small>Your password is protected before it is stored</small></div>
            </article>
            <article>
              <span><Icon name="database" size={19}/></span>
              <div><strong>Privacy-focused</strong><small>Sign-in details are not stored on this device</small></div>
            </article>
          </div>

          <div className="auth-register-note">
            <div className="auth-register-note__head">
              <span><Icon name="check" size={16}/> Simple setup</span>
              <strong>READY</strong>
            </div>
            <ul>
              <li>You can start using HeartTrack as soon as your account is created.</li>
              <li>Your sign-in details are not stored on this device.</li>
              <li>You can update your name and email later from Profile.</li>
            </ul>
          </div>
        </div>

        <div className="auth-login-footer">
          <span><Icon name="shield" size={16}/> Your session stays private</span>
          <span>For informational use only · not a medical diagnosis</span>
        </div>
      </section>

      <section className="auth-panel auth-register-panel">
        <div className="auth-panel__inner auth-register-card">
          <div className="auth-mobile-brand"><Brand /></div>
          <div className="auth-heading">
            <span className="auth-step">CREATE ACCOUNT</span>
            <h2>Create your account</h2>
            <p>Add a few details to get started.</p>
          </div>

          <form className="auth-form auth-form--register" onSubmit={submit}>
            <label className="field-label">Full name
              <div className="auth-input">
                <Icon name="user" size={17}/>
                <input value={form.full_name} onChange={set('full_name')} placeholder="Your full name" minLength={2} maxLength={80} required />
              </div>
            </label>

            <label className="field-label">Email address
              <div className="auth-input">
                <span>@</span>
                <input value={form.email} onChange={set('email')} type="email" placeholder="name@example.com" required />
              </div>
            </label>

            <label className="field-label">Create password
              <div className="auth-input">
                <Icon name="lock" size={17}/>
                <input value={form.password} onChange={set('password')} type={show ? 'text' : 'password'} placeholder="10+ characters" required />
                <button type="button" onClick={() => setShow((v) => !v)}><Icon name="eye" size={18}/></button>
              </div>
            </label>

            <div className="strength-meter">
              <div className="strength-bars">{[1,2,3,4].map((n) => <span className={strength >= n ? 'on' : ''} key={n}/> )}</div>
              <small>{strength === 4 ? 'Strong password' : 'Uppercase · lowercase · number · 10+ chars'}</small>
            </div>

            <label className="field-label">Confirm password
              <div className="auth-input">
                <Icon name="lock" size={17}/>
                <input value={form.confirm} onChange={set('confirm')} type={show ? 'text' : 'password'} placeholder="Repeat password" required />
              </div>
            </label>

            {error && <div className="form-error"><Icon name="info" size={17}/><span>{error}</span></div>}
            <button className="primary-auth-btn" disabled={busy}>{busy ? <span className="spinner"/> : <>Create account <Icon name="arrow" size={18}/></>}</button>
          </form>

          <div className="auth-back">Already have an account? <Link to="/login">Sign in</Link></div>
        </div>
      </section>
    </div>
  )
}
