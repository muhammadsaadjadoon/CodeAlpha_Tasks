import { useEffect, useMemo, useState } from 'react';
import {
  BookOpenCheck,
  BrainCircuit,
  ChevronRight,
  History,
  LogOut,
  Moon,
  ScanText,
  Sun,
  UserRound,
} from 'lucide-react';
import { api } from './api';
import { Brand } from './components/Brand';
import { UserAvatar } from './components/UserAvatar';
import { AccountPage } from './pages/AccountPage';
import { AuthPage } from './pages/AuthPage';
import { GuidePage } from './pages/GuidePage';
import { HistoryPage } from './pages/HistoryPage';
import { ModelLabPage } from './pages/ModelLabPage';
import { RecognizePage } from './pages/RecognizePage';
import type { Theme, User } from './types';

type View = 'recognize' | 'history' | 'models' | 'guide' | 'account';

const navigation = [
  { id: 'recognize' as const, label: 'Recognition', detail: 'Read handwriting', icon: ScanText },
  { id: 'history' as const, label: 'History', detail: 'Saved results', icon: History },
  { id: 'models' as const, label: 'Model Lab', detail: 'CNN intelligence', icon: BrainCircuit },
  { id: 'guide' as const, label: 'Guide', detail: 'Input guidance', icon: BookOpenCheck },
  { id: 'account' as const, label: 'Account', detail: 'Profile & privacy', icon: UserRound },
];

const viewMeta: Record<View, { eyebrow: string; title: string; copy: string }> = {
  recognize: {
    eyebrow: 'Recognition workspace',
    title: 'Recognition Studio',
    copy: 'Prepare a handwritten character and run the registered CNN with a clean, focused workflow.',
  },
  history: {
    eyebrow: 'Private archive',
    title: 'Recognition History',
    copy: 'Review saved prediction metadata while keeping source handwriting out of your archive.',
  },
  models: {
    eyebrow: 'Model intelligence',
    title: 'Model Laboratory',
    copy: 'Inspect registered MNIST and EMNIST checkpoints, readiness and evaluation evidence.',
  },
  guide: {
    eyebrow: 'Input quality',
    title: 'Recognition Guide',
    copy: 'Practical framing, contrast and mode guidance for more reliable character predictions.',
  },
  account: {
    eyebrow: 'Account workspace',
    title: 'Profile & Preferences',
    copy: 'Manage your identity, security and reading environment from one private workspace.',
  },
};

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>('recognize');
  const [revision, setRevision] = useState(0);
  const [theme, setTheme] = useState<Theme>('system');
  const [systemDark, setSystemDark] = useState(
    () => matchMedia('(prefers-color-scheme: dark)').matches,
  );

  useEffect(() => {
    api
      .me()
      .then((currentUser) => {
        setUser(currentUser);
        setTheme(currentUser.theme);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const media = matchMedia('(prefers-color-scheme: dark)');
    const change = () => setSystemDark(media.matches);
    media.addEventListener('change', change);
    return () => media.removeEventListener('change', change);
  }, []);

  const effectiveTheme = useMemo(
    () => (theme === 'system' ? (systemDark ? 'dark' : 'light') : theme),
    [theme, systemDark],
  );

  useEffect(() => {
    document.documentElement.dataset.theme = effectiveTheme;
  }, [effectiveTheme]);

  async function updateTheme(nextTheme: Theme) {
    if (!user) return;
    const updated = await api.updateTheme(nextTheme);
    setUser(updated);
    setTheme(updated.theme);
  }

  async function logout() {
    await api.logout();
    setUser(null);
    setTheme('system');
    setView('recognize');
  }

  if (loading) {
    return (
      <div className="wl-splash">
        <Brand theme={theme} className="splash-brand" />
        <div className="splash-loader" aria-label="Loading WriteLens">
          <i />
          <i />
          <i />
        </div>
        <p>Preparing your handwriting workspace…</p>
      </div>
    );
  }

  // IMPORTANT: Login/register screen is intentionally unchanged.
  if (!user) {
    return (
      <AuthPage
        theme={theme}
        onUser={(signedInUser) => {
          setUser(signedInUser);
          setTheme(signedInUser.theme);
        }}
      />
    );
  }

  const current = viewMeta[view];
  const currentNav = navigation.find((item) => item.id === view) ?? navigation[0];
  const CurrentIcon = currentNav.icon;

  return (
    <div className="wl-app post-login-v4">
      <aside className="wl-sidebar">
        <button
          className="sidebar-brand-button"
          type="button"
          onClick={() => setView('recognize')}
          aria-label="Open Recognition Studio"
        >
          <Brand theme={theme} className="sidebar-brand" />
        </button>

        <div className="sidebar-intro">
          <span>Workspace</span>
          <strong>Handwriting intelligence</strong>
        </div>

        <nav className="wl-sidenav" aria-label="WriteLens workspace">
          {navigation.map(({ id, label, detail, icon: Icon }, index) => (
            <button
              type="button"
              key={id}
              className={view === id ? 'active' : ''}
              onClick={() => setView(id)}
              aria-current={view === id ? 'page' : undefined}
            >
              <span className="sidenav-index">{String(index + 1).padStart(2, '0')}</span>
              <span className="sidenav-icon"><Icon /></span>
              <span className="sidenav-copy">
                <strong>{label}</strong>
                <small>{detail}</small>
              </span>
              <ChevronRight className="sidenav-arrow" />
            </button>
          ))}
        </nav>
<div className="sidebar-footer">
          <button
            type="button"
            className={`sidebar-account ${view === 'account' ? 'active' : ''}`}
            onClick={() => setView('account')}
          >
            <UserAvatar user={user} className="sidebar-avatar" />
            <span className="sidebar-account-copy">
              <strong>{user.full_name}</strong>
              <small>{user.email}</small>
            </span>
            <ChevronRight />
          </button>

          <div className="sidebar-footer-actions">
            <button
              type="button"
              onClick={() => updateTheme(effectiveTheme === 'dark' ? 'light' : 'dark')}
              title={effectiveTheme === 'dark' ? 'Use light theme' : 'Use dark theme'}
            >
              {effectiveTheme === 'dark' ? <Sun /> : <Moon />}
              <span>{effectiveTheme === 'dark' ? 'Light' : 'Dark'}</span>
            </button>
            <button type="button" onClick={logout} title="Sign out">
              <LogOut />
              <span>Sign out</span>
            </button>
          </div>
        </div>
      </aside>

      <section className="wl-workspace">
        <header className="workspace-header">
          <div className="workspace-title workspace-title-v4">
            <span className="workspace-title-icon"><CurrentIcon /></span>
            <span className="workspace-title-copy">
              <small>{current.eyebrow}</small>
              <strong>{current.title}</strong>
            </span>
          </div>

          <div className="workspace-header-actions">
            <span className="workspace-status"><i /> Ready</span>
            <button
              type="button"
              className="workspace-theme"
              onClick={() => updateTheme(effectiveTheme === 'dark' ? 'light' : 'dark')}
              aria-label={effectiveTheme === 'dark' ? 'Use light theme' : 'Use dark theme'}
            >
              {effectiveTheme === 'dark' ? <Sun /> : <Moon />}
            </button>
            <button
              type="button"
              className="workspace-avatar"
              onClick={() => setView('account')}
              aria-label="Open account"
            >
              <UserAvatar user={user} className="top-avatar" />
            </button>
          </div>
        </header>

        <main className="wl-main">
          <div className="workspace-page-intro">
            <span>{current.eyebrow}</span>
            <p>{current.copy}</p>
          </div>

          {view === 'recognize' ? (
            <RecognizePage onCreated={() => setRevision((value) => value + 1)} />
          ) : view === 'history' ? (
            <HistoryPage revision={revision} />
          ) : view === 'models' ? (
            <ModelLabPage />
          ) : view === 'guide' ? (
            <GuidePage />
          ) : (
            <AccountPage user={user} onTheme={updateTheme} onUser={setUser} />
          )}
        </main>
      </section>
    </div>
  );
}
