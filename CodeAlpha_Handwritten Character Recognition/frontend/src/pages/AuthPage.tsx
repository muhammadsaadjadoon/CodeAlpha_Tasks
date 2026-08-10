import { useState } from 'react';
import {
  ArrowRight,
  Eye,
  EyeOff,
  ScanText,
  ShieldCheck,
} from 'lucide-react';
import { api } from '../api';
import { Brand } from '../components/Brand';
import type { Theme, User } from '../types';

export function AuthPage({
  theme,
  onUser,
}: {
  theme: Theme;
  onUser: (user: User) => void;
}) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError('');

    try {
      const signedIn =
        mode === 'login'
          ? await api.login(email, password)
          : await api.register(fullName, email, password);
      onUser(signedIn);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Authentication failed.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-backdrop" aria-hidden="true">
        <span className="ink-orbit orbit-a" />
        <span className="ink-orbit orbit-b" />
        <span className="paper-line line-a" />
        <span className="paper-line line-b" />
      </div>

      <header className="auth-masthead">
        <Brand theme={theme} className="auth-main-brand" />
        <span className="auth-security"><ShieldCheck /> Private handwriting workspace</span>
      </header>

      <main className="auth-stage">
        <section className="auth-showcase">
          <span className="auth-kicker">Handwriting intelligence</span>
          <h1>From a handwritten mark to a confident character.</h1>
          <p>
            Upload an image or write directly on the canvas. WriteLens prepares the input,
            runs the appropriate CNN, and keeps the original handwriting out of history.
          </p>

          <div className="auth-demo-card">
            <div className="demo-paper">
              <span className="demo-character">Aa</span>
              <i className="demo-stroke stroke-one" />
              <i className="demo-stroke stroke-two" />
            </div>
            <div className="demo-readout">
              <span><ScanText /> Recognition pipeline</span>
              <strong>MNIST + EMNIST</strong>
              <small>Digits, uppercase and lowercase characters</small>
            </div>
          </div>

        </section>

        <section className="auth-form-shell">
          <div className="auth-mode-switch">
            <button
              type="button"
              className={mode === 'login' ? 'active' : ''}
              onClick={() => {
                setMode('login');
                setError('');
              }}
            >
              Sign in
            </button>
            <button
              type="button"
              className={mode === 'register' ? 'active' : ''}
              onClick={() => {
                setMode('register');
                setError('');
              }}
            >
              Create account
            </button>
          </div>

          <form className="auth-form" onSubmit={submit}>
            <span className="section-kicker">Secure access</span>
            <h2>{mode === 'login' ? 'Welcome to WriteLens' : 'Create your workspace'}</h2>
            <p>
              {mode === 'login'
                ? 'Continue to your recognition studio and private result archive.'
                : 'Your profile, theme and recognition metadata are stored by the backend.'}
            </p>

            {mode === 'register' && (
              <label className="field">
                <span>Full name</span>
                <input
                  required
                  minLength={2}
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  placeholder="Your name"
                  autoComplete="name"
                />
              </label>
            )}

            <label className="field">
              <span>Email address</span>
              <input
                required
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
              />
            </label>

            <label className="field">
              <span>Password</span>
              <div className="password-field">
                <input
                  required
                  minLength={8}
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Minimum 8 characters"
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((visible) => !visible)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff /> : <Eye />}
                </button>
              </div>
            </label>

            {error && <div className="form-error">{error}</div>}

            <button className="ink-primary full" disabled={busy}>
              <span>{busy ? 'Please wait…' : mode === 'login' ? 'Enter WriteLens' : 'Create account'}</span>
              <ArrowRight />
            </button>

            <div className="auth-form-foot">
              <ShieldCheck />
              <span>Session authentication uses a secure HttpOnly cookie.</span>
            </div>
          </form>
        </section>
      </main>
    </div>
  );
}
