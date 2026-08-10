import { useEffect, useMemo, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import Brand from './Brand.jsx'
import { Icon } from './Icons.jsx'

const sections = [
  { label: 'Workspace', items: [
    { to: '/app', end: true, icon: 'grid', label: 'Overview', hint: 'Your heart-risk workspace' },
    { to: '/app/assessment', icon: 'pulse', label: 'New Assessment', hint: 'Start a new risk check' },
    { to: '/app/cases', icon: 'users', label: 'Session Cases', hint: 'Assessments from this session' },
  ]},
  { label: 'Intelligence', items: [
    { to: '/app/models', icon: 'brain', label: 'Model Center', hint: 'Compare model performance' },
    { to: '/app/dataset', icon: 'database', label: 'Dataset Lab', hint: 'Explore the training data' },
    { to: '/app/guide', icon: 'book', label: 'Clinical Guide', hint: 'Understand each input' },
  ]},
  { label: 'Operations', items: [
    { to: '/app/reports', icon: 'file', label: 'Reports', hint: 'Print or export results' },
    { to: '/app/system', icon: 'activity', label: 'System Health', hint: 'Connection and privacy status' },
  ]},
  { label: 'Account', items: [
    { to: '/app/profile', icon: 'user', label: 'Profile', hint: 'Your account details' },
    { to: '/app/settings', icon: 'settings', label: 'Settings', hint: 'Workspace preferences' },
  ]},
]

const titleMap = {
  '/app': ['Overview', 'Your heart-risk workspace'],
  '/app/assessment': ['New Assessment', 'Enter patient details and calculate risk'],
  '/app/cases': ['Session Cases', 'Assessments from this session'],
  '/app/models': ['Model Center', 'Compare trained models and performance'],
  '/app/dataset': ['Dataset Lab', 'Explore the data used to train the models'],
  '/app/guide': ['Clinical Guide', 'Understand every assessment field'],
  '/app/reports': ['Reports', 'Print or export your session results'],
  '/app/system': ['System Health', 'Check connection and model status'],
  '/app/profile': ['Profile', 'Manage your account details'],
  '/app/settings': ['Settings', 'Adjust your workspace'],
}

export default function AppShell() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 30000)
    return () => clearInterval(timer)
  }, [])
  useEffect(() => setMobileOpen(false), [location.pathname])

  const current = useMemo(() => {
    if (location.pathname.startsWith('/app/assessment/result')) return ['Risk Result', 'Review the current assessment result']
    return titleMap[location.pathname] || ['HeartTrack', 'Heart-risk assessment workspace']
  }, [location.pathname])

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-frame">
      <button className="mobile-menu-btn" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Icon name="menu" /></button>
      <aside className={`sidebar ${mobileOpen ? 'sidebar--open' : ''}`}>
        <div className="sidebar__head">
          <Brand />
          <button className="sidebar__close" onClick={() => setMobileOpen(false)} aria-label="Close navigation"><Icon name="x" /></button>
        </div>
        <div className="sidebar__newcase">
          <button onClick={() => navigate('/app/assessment')}><span className="newcase-icon"><Icon name="plus" size={17}/></span><span><strong>New assessment</strong><small>13 clinical inputs</small></span><Icon name="chevron" size={16}/></button>
        </div>
        <nav className="sidebar__nav" aria-label="Application navigation">
          {sections.map((section) => (
            <div className="nav-group" key={section.label}>
              <div className="nav-group__label">{section.label}</div>
              {section.items.map((item) => (
                <NavLink key={item.to} to={item.to} end={item.end} className={({ isActive }) => `nav-item ${isActive ? 'nav-item--active' : ''}`}>
                  <span className="nav-item__icon"><Icon name={item.icon}/></span>
                  <span className="nav-item__copy"><strong>{item.label}</strong><small>{item.hint}</small></span>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar__footer">
          <div className="secure-pill"><span className="secure-dot"/>Secure session</div>
          <div className="user-card">
            <div className="avatar">{(user?.display_name || 'H').split(' ').map((n) => n[0]).slice(0,2).join('')}</div>
            <div className="user-card__copy"><strong>{user?.display_name}</strong><small>{user?.email}</small></div>
            <button onClick={handleLogout} aria-label="Sign out" title="Sign out"><Icon name="logout" size={18}/></button>
          </div>
        </div>
      </aside>
      {mobileOpen && <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}

      <main className="main-shell">
        <header className="topbar">
          <div className="topbar__title"><span className="eyebrow">HeartTrack / Workspace</span><h1>{current[0]}</h1><p>{current[1]}</p></div>
          <div className="topbar__right">
            <div className="runtime-chip runtime-chip--simple"><span className="runtime-chip__dot"/><strong>Online</strong></div>
            <div className="time-chip"><strong>{time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</strong><small>{time.toLocaleDateString([], { day: '2-digit', month: 'short' })}</small></div>
          </div>
        </header>
        <section className="workspace"><Outlet /></section>
      </main>
    </div>
  )
}
