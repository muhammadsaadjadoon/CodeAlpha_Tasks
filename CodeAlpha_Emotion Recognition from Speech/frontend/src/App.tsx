import { useEffect, useMemo, useState } from 'react';
import {
  BookOpen,
  BrainCircuit,
  ChevronRight,
  History,
  LogOut,
  Mic2,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Sun,
  UserRound,
} from 'lucide-react';
import { api } from './api';
import { Brand } from './components/Brand';
import { UserAvatar } from './components/UserAvatar';
import { AccountPage } from './pages/AccountPage';
import { AnalyzePage } from './pages/AnalyzePage';
import { AuthPage } from './pages/AuthPage';
import { HistoryPage } from './pages/HistoryPage';
import { GuidePage } from './pages/GuidePage';
import { InsightsPage } from './pages/InsightsPage';
import type { AnalysisResult, ModelStatus, Theme, User } from './types';

type View = 'analyze' | 'history' | 'guide' | 'insights' | 'account';

const viewMeta: Record<View, { eyebrow: string; title: string; description: string }> = {
  analyze: {
    eyebrow: 'Voice workspace',
    title: 'Analyze speech',
    description: 'Record or upload a voice sample and review its emotional signal.',
  },
  history: {
    eyebrow: 'Private archive',
    title: 'Analysis history',
    description: 'Review saved result metadata without storing the original recordings.',
  },
  guide: {
    eyebrow: 'Voice guide',
    title: 'Recording guide',
    description: 'Practical steps for cleaner recordings and more reliable emotional analysis.',
  },
  insights: {
    eyebrow: 'Model transparency',
    title: 'System intelligence',
    description: 'Understand how INFLECT processes, evaluates, and protects every analysis.',
  },
  account: {
    eyebrow: 'Personal settings',
    title: 'Account & privacy',
    description: 'Manage your appearance preferences and review data safeguards.',
  },
};

export default function App() {
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const [view, setView] = useState<View>('analyze');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [historyRevision, setHistoryRevision] = useState(0);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null));
  }, []);

  const theme: Theme = user?.theme || 'system';
  const effectiveTheme = useMemo(
    () => theme === 'system'
      ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : theme,
    [theme],
  );

  useEffect(() => {
    document.documentElement.dataset.theme = effectiveTheme;
    document.documentElement.style.colorScheme = effectiveTheme;
  }, [effectiveTheme]);

  useEffect(() => {
    if (!user) return;
    api.modelStatus().then(setModelStatus).catch(() => setModelStatus(null));
  }, [user]);

  if (user === undefined) {
    return <div className="splash">
      <div className="splash-logo"><Brand theme="dark"/></div>
      <div className="splash-loader"><span/><span/><span/></div>
      <p>Preparing your private workspace</p>
    </div>;
  }

  if (!user) return <AuthPage onAuth={setUser} theme={theme}/>;

  async function logout() {
    await api.logout();
    setUser(null);
  }

  async function updateTheme(next: Theme) {
    setUser(await api.updateTheme(next));
  }

  function analysisCreated(_: AnalysisResult) {
    setHistoryRevision(value => value + 1);
    api.modelStatus().then(setModelStatus).catch(() => undefined);
  }

  const initials = user.full_name
    .split(' ')
    .filter(Boolean)
    .map(value => value[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  const nav = [
    { id: 'analyze' as const, label: 'Analyze', caption: 'Record or upload', icon: Mic2 },
    { id: 'history' as const, label: 'History', caption: 'Saved results', icon: History },
    { id: 'guide' as const, label: 'Guide', caption: 'Recording help', icon: BookOpen },
    { id: 'insights' as const, label: 'Intelligence', caption: 'Model details', icon: BrainCircuit },
    { id: 'account' as const, label: 'Account', caption: 'Theme & privacy', icon: UserRound },
  ];

  const statusLabel = modelStatus?.ready
    ? 'Ready for analysis'
    : modelStatus?.state === 'error'
      ? 'Model needs attention'
      : 'Preparing model';

  return <div className={`app-shell ${sidebarOpen ? '' : 'sidebar-collapsed'}`}>
    <aside className="sidebar">
      <div className="sidebar-top">
        <div className="sidebar-brand">
          <Brand theme={theme} compact/>
          <button
            type="button"
            className="collapse-button"
            onClick={() => setSidebarOpen(value => !value)}
            aria-label={sidebarOpen ? 'Collapse navigation' : 'Expand navigation'}
          >
            {sidebarOpen ? <PanelLeftClose/> : <PanelLeftOpen/>}
          </button>
        </div>

        <div className="sidebar-section-label">Workspace</div>
        <nav className="primary-nav" aria-label="Primary navigation">
          {nav.map(({ id, label, caption, icon: Icon }) => <button
            key={id}
            type="button"
            className={view === id ? 'active' : ''}
            onClick={() => setView(id)}
            title={label}
          >
            <span className="nav-icon"><Icon/></span>
            <span className="nav-copy"><strong>{label}</strong><small>{caption}</small></span>
            <ChevronRight className="nav-chevron"/>
          </button>)}
        </nav>
      </div>

      <div className="sidebar-bottom">
        <button type="button" className="user-card" onClick={() => setView('account')}>
          <UserAvatar user={user} className="avatar"/>
          <span className="user-card-copy"><strong>{user.full_name}</strong><small>{user.email}</small></span>
        </button>

        <div className="sidebar-utilities">
          <button
            type="button"
            onClick={() => updateTheme(effectiveTheme === 'dark' ? 'light' : 'dark')}
            title={effectiveTheme === 'dark' ? 'Use light theme' : 'Use dark theme'}
          >
            {effectiveTheme === 'dark' ? <Sun/> : <Moon/>}
            <span>{effectiveTheme === 'dark' ? 'Light theme' : 'Dark theme'}</span>
          </button>
          <button type="button" className="signout" onClick={logout}>
            <LogOut/><span>Sign out</span>
          </button>
        </div>
      </div>
    </aside>

    <main className="workspace-shell">
      <header className="workspace-header">
        <div className="workspace-title">
          <span>{viewMeta[view].eyebrow}</span>
          <div><h1>{viewMeta[view].title}</h1><p>{viewMeta[view].description}</p></div>
        </div>
        <div className="header-actions">
          <div className={`model-pill state-${modelStatus?.state || 'loading'}`}>
            <i/>
            <span>{statusLabel}</span>
          </div>
          <button type="button" className="header-avatar" onClick={() => setView('account')} aria-label="Open account">
            <UserAvatar user={user} className="header-avatar-image"/>
          </button>
        </div>
      </header>

      <div className="workspace-scroll">
        {view === 'analyze'
          ? <AnalyzePage onAnalysisCreated={analysisCreated}/>
          : view === 'history'
            ? <HistoryPage revision={historyRevision}/>
            : view === 'guide'
              ? <GuidePage/>
              : view === 'insights'
              ? <InsightsPage modelStatus={modelStatus}/>
              : <AccountPage user={user} onTheme={updateTheme} onUser={setUser}/>}
      </div>
    </main>
  </div>;
}
