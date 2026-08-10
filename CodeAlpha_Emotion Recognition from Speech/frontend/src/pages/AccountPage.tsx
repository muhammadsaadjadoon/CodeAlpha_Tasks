import { useEffect, useRef, useState } from 'react';
import {
  ImagePlus,
  Laptop,
  LockKeyhole,
  Moon,
  ShieldCheck,
  Sun,
  Trash2,
  UserRound,
} from 'lucide-react';
import { api } from '../api';
import { UserAvatar } from '../components/UserAvatar';
import type { Theme, User } from '../types';
import '../profile-storage.css';

export function AccountPage({
  user,
  onTheme,
  onUser,
}: {
  user: User;
  onTheme: (theme: Theme) => void;
  onUser?: (user: User) => void;
}) {
  const [profileUser, setProfileUser] = useState(user);
  const [avatarBusy, setAvatarBusy] = useState(false);
  const [avatarMessage, setAvatarMessage] = useState('');
  const [avatarError, setAvatarError] = useState('');
  const avatarInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setProfileUser(user);
  }, [user]);

  useEffect(() => {
    api.me()
      .then(next => {
        setProfileUser(next);
        onUser?.(next);
      })
      .catch(() => undefined);
  }, []);

  function applyUser(next: User) {
    setProfileUser(next);
    onUser?.(next);
  }

  async function uploadAvatar(file?: File) {
    if (!file) return;

    setAvatarError('');
    setAvatarMessage('');

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setAvatarError('Choose a JPEG, PNG, or WebP image.');
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      setAvatarError('Profile image must be 2 MB or smaller.');
      return;
    }

    setAvatarBusy(true);
    try {
      const next = await api.uploadAvatar(file);
      applyUser(next);
      setAvatarMessage('Profile image saved securely in the backend.');
    } catch (reason) {
      setAvatarError(reason instanceof Error ? reason.message : 'Profile image could not be saved.');
    } finally {
      setAvatarBusy(false);
      if (avatarInput.current) avatarInput.current.value = '';
    }
  }

  async function removeAvatar() {
    setAvatarBusy(true);
    setAvatarError('');
    setAvatarMessage('');
    try {
      const next = await api.deleteAvatar();
      applyUser(next);
      setAvatarMessage('Profile image removed from the backend.');
    } catch (reason) {
      setAvatarError(reason instanceof Error ? reason.message : 'Profile image could not be removed.');
    } finally {
      setAvatarBusy(false);
    }
  }

  const themes = [
    ['system', Laptop, 'System', 'Match your device appearance'],
    ['light', Sun, 'Light', 'Bright, focused workspace'],
    ['dark', Moon, 'Dark', 'Low-glare working environment'],
  ] as const;

  return <div className="page-stack account-page">
    <section className="account-hero">
      <div>
        <span className="eyebrow"><UserRound/>Personal workspace</span>
        <h2>Account, appearance, and privacy.</h2>
        <p>Your profile image, account preference, and analysis history are stored in the backend—not browser storage.</p>
      </div>
    </section>

    <section className="account-layout">
      <article className="panel identity-card">
        <UserAvatar user={profileUser} className="profile-avatar"/>
        <div className="profile-photo-actions">
          <input
            ref={avatarInput}
            type="file"
            hidden
            accept="image/jpeg,image/png,image/webp"
            onChange={event => uploadAvatar(event.target.files?.[0])}
          />
          <button
            type="button"
            className="secondary-action"
            onClick={() => avatarInput.current?.click()}
            disabled={avatarBusy}
          >
            <ImagePlus/>{avatarBusy ? 'Saving…' : profileUser.has_avatar ? 'Replace photo' : 'Upload photo'}
          </button>
          {profileUser.has_avatar && <button
            type="button"
            className="text-action danger"
            onClick={removeAvatar}
            disabled={avatarBusy}
          >
            <Trash2/>Remove
          </button>}
        </div>
        <p className="profile-photo-note">JPEG, PNG, or WebP · maximum 2 MB · saved directly to the backend database</p>
        {avatarMessage && <div className="profile-storage-message success">{avatarMessage}</div>}
        {avatarError && <div className="profile-storage-message danger">{avatarError}</div>}

        <div className="identity-copy">
          <span className="section-kicker">Signed in as</span>
          <h3>{profileUser.full_name}</h3>
          <p>{profileUser.email}</p>
        </div>
        <div className="account-status"><ShieldCheck/><span>Protected authenticated session</span></div>
      </article>

      <article className="panel preference-card">
        <div className="preference-header">
          <div><span className="section-kicker">Appearance</span><h3>Choose your workspace theme</h3><p>The selected preference is saved securely with your backend account.</p></div>
        </div>
        <div className="theme-options">
          {themes.map(([theme, Icon, title, text]) => <button
            type="button"
            key={theme}
            className={profileUser.theme === theme ? 'active' : ''}
            onClick={async () => {
              await onTheme(theme);
              const next = await api.me();
              applyUser(next);
            }}
          >
            <span className="theme-icon"><Icon/></span>
            <span><strong>{title}</strong><small>{text}</small></span>
            <i/>
          </button>)}
        </div>
      </article>
    </section>

    <section className="privacy-grid">
      <article className="panel">
        <span><LockKeyhole/></span>
        <div><h3>No browser persistence</h3><p>Profile, theme, and analysis data are not written to localStorage, sessionStorage, or IndexedDB.</p></div>
      </article>
      <article className="panel">
        <span><ShieldCheck/></span>
        <div><h3>No retained recordings</h3><p>Uploaded and recorded voice files are removed immediately after inference completes.</p></div>
      </article>
      <article className="panel">
        <span><UserRound/></span>
        <div><h3>Backend-owned profile</h3><p>Your profile image, account information, and result history remain attached to your authenticated backend account.</p></div>
      </article>
    </section>
  </div>;
}
