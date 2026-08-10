import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { Icon } from '../components/Icons.jsx'

export default function Profile(){
  const { user, updateProfile } = useAuth()
  const [editing, setEditing] = useState(false)
  const [displayName, setDisplayName] = useState(user?.display_name || '')
  const [email, setEmail] = useState(user?.email || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    setDisplayName(user?.display_name || '')
    setEmail(user?.email || '')
  }, [user])

  const initials = (user?.display_name || 'HeartTrack Analyst').split(' ').map(x => x[0]).slice(0,2).join('')

  function cancelEdit(){
    setDisplayName(user?.display_name || '')
    setEmail(user?.email || '')
    setError('')
    setSaved(false)
    setEditing(false)
  }

  async function saveProfile(event){
    event.preventDefault()
    setError('')
    setSaved(false)
    if (displayName.trim().length < 2) { setError('Enter a valid display name.'); return }
    if (!email.trim()) { setError('Enter a valid email address.'); return }
    setSaving(true)
    try {
      await updateProfile(displayName.trim(), email.trim())
      setSaved(true)
      setEditing(false)
      window.setTimeout(() => setSaved(false), 2400)
    } catch (err) {
      setError(err.message || 'Unable to update profile.')
    } finally {
      setSaving(false)
    }
  }

  return <div className="page-stack">
    <section className="profile-card">
      <div className="profile-avatar">{initials}</div>
      <div className="profile-card__copy">
        <span className="section-kicker">YOUR PROFILE</span>
        <h2>{user?.display_name}</h2>
        <p>{user?.email}</p>
        <div className="profile-badges"><span><Icon name="shield" size={14}/>Signed in</span><span><Icon name="lock" size={14}/>Secure session</span></div>
      </div>
    </section>

    <div className="profile-grid">
      <section className="panel profile-identity-panel">
        <div className="panel-head profile-panel-head">
          <div><span className="section-kicker">ACCOUNT</span><h3>Profile details</h3></div>
          {!editing && <button className="profile-edit-btn" type="button" onClick={() => { setEditing(true); setError(''); setSaved(false) }}>Edit profile</button>}
        </div>

        {editing ? (
          <form className="profile-edit-form" onSubmit={saveProfile}>
            <label>
              <span>Display name</span>
              <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} maxLength={80} autoComplete="name" />
            </label>
            <label>
              <span>Email</span>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
            </label>
            <div className="profile-static-row"><span>Role</span><strong>HeartTrack Analyst</strong></div>
            <div className="profile-static-row"><span>Saved on this device</span><strong>No</strong></div>
            {error && <div className="profile-form-message profile-form-message--error">{error}</div>}
            <div className="profile-form-actions">
              <button className="profile-cancel-btn" type="button" onClick={cancelEdit} disabled={saving}>Cancel</button>
              <button className="profile-save-btn" type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save changes'}</button>
            </div>
          </form>
        ) : (
          <>
            <div className="audit-list">
              <div><span>Display name</span><strong>{user?.display_name}</strong></div>
              <div><span>Email</span><strong>{user?.email}</strong></div>
              <div><span>Role</span><strong>HeartTrack Analyst</strong></div>
              <div><span>Saved on this device</span><strong>No</strong></div>
            </div>
            {saved && <div className="profile-form-message profile-form-message--success"><Icon name="check" size={15}/> Profile updated</div>}
          </>
        )}
      </section>

      <section className="panel">
        <div className="panel-head"><div><span className="section-kicker">SECURITY</span><h3>Sign-in protection</h3></div></div>
        <div className="security-cards">
          <div><span><Icon name="shield"/></span><p><strong>Secure sign-in</strong><small>Your sign-in session is protected by the server.</small></p></div>
          <div><span><Icon name="lock"/></span><p><strong>Private sign-in</strong><small>Your sign-in details are not stored on this device.</small></p></div>
        </div>
      </section>
    </div>

    <div className="safety-banner"><Icon name="info"/><div><strong>About your account</strong><p>Accounts created here are session-based and may be cleared when HeartTrack restarts.</p></div></div>
  </div>
}
