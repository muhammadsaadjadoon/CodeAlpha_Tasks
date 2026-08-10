import { useEffect, useRef, useState } from 'react';
import {
  Camera,
  Check,
  Database,
  KeyRound,
  Laptop,
  LockKeyhole,
  Mail,
  Moon,
  PencilLine,
  Save,
  ShieldCheck,
  Sun,
  Trash2,
  UserRound,
  X,
} from 'lucide-react';
import { api } from '../api';
import { UserAvatar } from '../components/UserAvatar';
import type { Theme, User } from '../types';

export function AccountPage({
  user,
  onTheme,
  onUser,
}: {
  user: User;
  onTheme: (theme: Theme) => void;
  onUser: (user: User) => void;
}) {
  const fileInput = useRef<HTMLInputElement>(null);

  const [avatarBusy, setAvatarBusy] = useState(false);
  const [editingName, setEditingName] = useState(false);
  const [nameDraft, setNameDraft] = useState(user.full_name);
  const [nameBusy, setNameBusy] = useState(false);
  const [nameMessage, setNameMessage] = useState('');

  const [passwordOpen, setPasswordOpen] = useState(false);
  const [passwordBusy, setPasswordBusy] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMessage, setPasswordMessage] = useState('');

  useEffect(() => {
    setNameDraft(user.full_name);
  }, [user.full_name]);

  async function uploadAvatar(file?: File) {
    if (!file) return;
    setAvatarBusy(true);
    try {
      onUser(await api.uploadAvatar(file));
    } finally {
      setAvatarBusy(false);
      if (fileInput.current) fileInput.current.value = '';
    }
  }

  async function removeAvatar() {
    setAvatarBusy(true);
    try {
      onUser(await api.deleteAvatar());
    } finally {
      setAvatarBusy(false);
    }
  }

  async function saveName(event: React.FormEvent) {
    event.preventDefault();
    const clean = nameDraft.trim().replace(/\s+/g, ' ');
    if (clean.length < 2) {
      setNameMessage('Use at least 2 characters.');
      return;
    }
    if (clean === user.full_name) {
      setEditingName(false);
      setNameMessage('');
      return;
    }

    setNameBusy(true);
    setNameMessage('');
    try {
      const updated = await api.updateName(clean);
      onUser(updated);
      setNameDraft(updated.full_name);
      setEditingName(false);
      setNameMessage('Username updated successfully.');
    } catch (reason) {
      setNameMessage(reason instanceof Error ? reason.message : 'Could not update username.');
    } finally {
      setNameBusy(false);
    }
  }

  function closePassword() {
    setPasswordOpen(false);
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  }

  async function changePassword(event: React.FormEvent) {
    event.preventDefault();
    setPasswordMessage('');

    if (newPassword.length < 8) {
      setPasswordMessage('New password must contain at least 8 characters.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordMessage('New password and confirmation do not match.');
      return;
    }

    setPasswordBusy(true);
    try {
      await api.updatePassword(currentPassword, newPassword);
      closePassword();
      setPasswordMessage('Password updated securely.');
    } catch (reason) {
      setPasswordMessage(reason instanceof Error ? reason.message : 'Could not update password.');
    } finally {
      setPasswordBusy(false);
    }
  }

  const themes: [Theme, typeof Laptop, string, string][] = [
    ['system', Laptop, 'System', 'Follow your device appearance'],
    ['light', Sun, 'Light', 'Bright paper-inspired workspace'],
    ['dark', Moon, 'Dark', 'Deep ink workspace with low glare'],
  ];

  return (
    <div className="wl-page account-page account-page-v4">
      <section className="page-hero account-hero-v4">
        <div className="hero-copy">
          <span className="hero-index">05 · Account</span>
          <h1>One place for your profile, security and interface preferences.</h1>
          <p>
            Identity, password, profile image and theme are managed through the backend.
            Personal account state is not written to browser persistence.
          </p>
        </div>
      </section>

      <section className="account-layout account-layout-v4">
        <article className="profile-card-v4">
          <header className="profile-card-heading">
            <div>
              <span className="section-kicker">Profile</span>
              <h2>Personal identity</h2>
            </div>
            <span className="profile-card-shield"><ShieldCheck /></span>
          </header>

          <section className="profile-identity-v4">
            <div className="profile-avatar-shell">
              <UserAvatar user={user} className="account-avatar-v4" />
              <button
                type="button"
                className="profile-avatar-camera"
                onClick={() => fileInput.current?.click()}
                disabled={avatarBusy}
                aria-label="Change profile photo"
              >
                <Camera />
              </button>
            </div>

            <div className="profile-identity-copy">
              <span>WriteLens member</span>
              <strong>{user.full_name}</strong>
              <small>{user.email}</small>
            </div>

            <div className="profile-photo-actions-v4">
              <button
                type="button"
                className="profile-photo-change"
                onClick={() => fileInput.current?.click()}
                disabled={avatarBusy}
              >
                <Camera />
                {avatarBusy ? 'Updating…' : user.avatar_version > 0 ? 'Change photo' : 'Add photo'}
              </button>
              {user.avatar_version > 0 && (
                <button
                  type="button"
                  className="profile-photo-delete"
                  onClick={removeAvatar}
                  disabled={avatarBusy}
                  aria-label="Remove profile photo"
                >
                  <Trash2 />
                </button>
              )}
            </div>

            <input
              ref={fileInput}
              hidden
              type="file"
              accept="image/png,image/jpeg,image/webp"
              onChange={(event) => uploadAvatar(event.target.files?.[0])}
            />
          </section>

          <section className="account-detail-list">
            <div className={`account-detail-item ${editingName ? 'open' : ''}`}>
              <div className="account-detail-summary">
                <span className="account-detail-icon"><UserRound /></span>
                <span className="account-detail-copy">
                  <small>Username</small>
                  <strong>{user.full_name}</strong>
                </span>
                <button
                  type="button"
                  className="account-detail-action"
                  onClick={() => {
                    setNameDraft(user.full_name);
                    setNameMessage('');
                    setEditingName((value) => !value);
                  }}
                >
                  {editingName ? <X /> : <PencilLine />}
                  {editingName ? 'Close' : 'Edit'}
                </button>
              </div>

              {editingName && (
                <form className="account-inline-form" onSubmit={saveName} autoComplete="off">
                  <label>
                    <span>New username</span>
                    <input
                      value={nameDraft}
                      minLength={2}
                      maxLength={120}
                      onChange={(event) => setNameDraft(event.target.value)}
                      autoComplete="off"
                    />
                  </label>
                  <button type="submit" disabled={nameBusy}>
                    <Save />
                    {nameBusy ? 'Saving…' : 'Save changes'}
                  </button>
                </form>
              )}
            </div>

            <div className="account-detail-item static">
              <div className="account-detail-summary">
                <span className="account-detail-icon"><Mail /></span>
                <span className="account-detail-copy">
                  <small>Email address</small>
                  <strong>{user.email}</strong>
                </span>
                <span className="account-detail-badge">Verified account</span>
              </div>
            </div>

            <div className={`account-detail-item ${passwordOpen ? 'open' : ''}`}>
              <div className="account-detail-summary">
                <span className="account-detail-icon"><KeyRound /></span>
                <span className="account-detail-copy">
                  <small>Password</small>
                  <strong>••••••••••••</strong>
                </span>
                <button
                  type="button"
                  className="account-detail-action"
                  onClick={() => {
                    setPasswordMessage('');
                    if (passwordOpen) closePassword();
                    else setPasswordOpen(true);
                  }}
                >
                  {passwordOpen ? <X /> : <PencilLine />}
                  {passwordOpen ? 'Close' : 'Change'}
                </button>
              </div>

              {passwordOpen && (
                <form className="account-password-form" onSubmit={changePassword} autoComplete="off">
                  <label>
                    <span>Current password</span>
                    <input
                      type="password"
                      required
                      minLength={8}
                      maxLength={128}
                      value={currentPassword}
                      onChange={(event) => setCurrentPassword(event.target.value)}
                      autoComplete="off"
                    />
                  </label>
                  <label>
                    <span>New password</span>
                    <input
                      type="password"
                      required
                      minLength={8}
                      maxLength={128}
                      value={newPassword}
                      onChange={(event) => setNewPassword(event.target.value)}
                      autoComplete="off"
                    />
                  </label>
                  <label>
                    <span>Confirm new password</span>
                    <input
                      type="password"
                      required
                      minLength={8}
                      maxLength={128}
                      value={confirmPassword}
                      onChange={(event) => setConfirmPassword(event.target.value)}
                      autoComplete="off"
                    />
                  </label>
                  <button type="submit" disabled={passwordBusy}>
                    <LockKeyhole />
                    {passwordBusy ? 'Updating…' : 'Update password'}
                  </button>
                </form>
              )}
            </div>
          </section>

          {(nameMessage || passwordMessage) && (
            <div className="account-feedback-v4">
              <ShieldCheck />
              <span>{nameMessage || passwordMessage}</span>
            </div>
          )}
        </article>

        <div className="account-side-v4">
          <section className="appearance-card appearance-card-v4">
            <div className="settings-heading">
              <span className="section-kicker">Appearance</span>
              <h2>Reading environment</h2>
              <p>Choose the visual mode that feels right. The preference follows your account.</p>
            </div>

            <div className="theme-choices theme-choices-v4">
              {themes.map(([value, Icon, title, description]) => (
                <button
                  type="button"
                  key={value}
                  className={user.theme === value ? 'active' : ''}
                  onClick={() => onTheme(value)}
                >
                  <span className="theme-choice-icon"><Icon /></span>
                  <span className="theme-choice-copy">
                    <strong>{title}</strong>
                    <small>{description}</small>
                  </span>
                  <span className="theme-choice-check">{user.theme === value && <Check />}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="account-privacy-v4">
            <header>
              <span className="section-kicker">Privacy architecture</span>
              <h2>Built around backend-owned state.</h2>
            </header>
            <div className="privacy-card-grid privacy-card-grid-v4">
              <article>
                <span><Database /></span>
                <div>
                  <strong>Backend history</strong>
                  <small>Prediction metadata remains in the application database.</small>
                </div>
              </article>
              <article>
                <span><LockKeyhole /></span>
                <div>
                  <strong>No raw-image archive</strong>
                  <small>Uploaded and drawn handwriting is not retained in history.</small>
                </div>
              </article>
              <article>
                <span><ShieldCheck /></span>
                <div>
                  <strong>Private session</strong>
                  <small>Authentication uses a server-validated HttpOnly cookie.</small>
                </div>
              </article>
            </div>
          </section>
        </div>
      </section>
    </div>
  );
}
