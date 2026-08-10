import { useState, type FormEvent } from 'react';
import {
  ArrowRight,
  AudioLines,
  Check,
  Eye,
  EyeOff,
  LockKeyhole,
  ShieldCheck,
  Waves,
} from 'lucide-react';
import { api } from '../api';
import { Brand } from '../components/Brand';
import type { Theme, User } from '../types';

export function AuthPage({ onAuth, theme }: { onAuth: (user: User) => void; theme: Theme }) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      onAuth(mode === 'login'
        ? await api.login(email, password)
        : await api.register(name, email, password));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Your workspace could not be opened.');
    } finally {
      setBusy(false);
    }
  }

  function switchMode() {
    setMode(value => value === 'login' ? 'register' : 'login');
    setError('');
  }

  return <main className="auth-shell">
    <section className="auth-story">
      <header className="auth-brand">
        <Brand theme={theme}/>
        <span>Speech emotion intelligence</span>
      </header>

      <div className="auth-story-content">
        <span className="eyebrow">Private voice analysis</span>
        <h1>Hear beyond words.</h1>
        <p>INFLECT turns speech into a clear emotional profile—without retaining the original recording.</p>

        <div className="auth-value-list">
          <article>
            <span><AudioLines/></span>
            <div><strong>Useful emotional context</strong><p>Leading emotion, confidence, probability distribution, valence, and activation.</p></div>
          </article>
          <article>
            <span><Waves/></span>
            <div><strong>Record or upload naturally</strong><p>Use your microphone in real time or analyze an existing voice sample.</p></div>
          </article>
          <article>
            <span><ShieldCheck/></span>
            <div><strong>Designed for privacy</strong><p>Original audio is processed temporarily and removed after inference.</p></div>
          </article>
        </div>
      </div>

      <footer className="auth-trust">
        <span><LockKeyhole/>Authenticated private workspace</span>
        <span><Check/>No browser-side data storage</span>
      </footer>
    </section>

    <section className="auth-panel">
      <form onSubmit={submit} className="auth-form">
        <div className="auth-form-head">
          <span className="section-kicker">{mode === 'login' ? 'Welcome back' : 'Create your workspace'}</span>
          <h2>{mode === 'login' ? 'Sign in to INFLECT' : 'Start analyzing voice'}</h2>
          <p>{mode === 'login'
            ? 'Enter your account details to continue.'
            : 'Create secure access to your private analysis workspace.'}</p>
        </div>

        {mode === 'register' && <label className="form-field">
          <span>Full name</span>
          <input
            value={name}
            onChange={event => setName(event.target.value)}
            required
            minLength={2}
            placeholder="Your full name"
            autoComplete="name"
          />
        </label>}

        <label className="form-field">
          <span>Email address</span>
          <input
            type="email"
            value={email}
            onChange={event => setEmail(event.target.value)}
            required
            placeholder="name@company.com"
            autoComplete="email"
          />
        </label>

        <label className="form-field">
          <span>Password</span>
          <div className="password-field">
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={event => setPassword(event.target.value)}
              required
              minLength={mode === 'register' ? 10 : 1}
              placeholder={mode === 'register' ? 'Minimum 10 characters' : 'Enter your password'}
              autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
            />
            <button type="button" onClick={() => setShowPassword(value => !value)} aria-label={showPassword ? 'Hide password' : 'Show password'}>
              {showPassword ? <EyeOff/> : <Eye/>}
            </button>
          </div>
        </label>

        {error && <div className="inline-alert danger" role="alert">{error}</div>}

        <button className="primary-action full auth-submit" disabled={busy}>
          <span>{busy ? 'Opening workspace…' : mode === 'login' ? 'Sign in securely' : 'Create account'}</span>
          <ArrowRight/>
        </button>

        <div className="auth-switch">
          <span>{mode === 'login' ? 'New to INFLECT?' : 'Already have an account?'}</span>
          <button type="button" onClick={switchMode}>{mode === 'login' ? 'Create an account' : 'Sign in instead'}</button>
        </div>

        <div className="auth-security-note">
          <ShieldCheck/>
          <p>Your session is protected using an HttpOnly authentication cookie.</p>
        </div>
      </form>
    </section>
  </main>;
}
