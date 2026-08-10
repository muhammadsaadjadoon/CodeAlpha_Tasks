import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import type { User } from '../types';

function initials(name: string) {
  return name
    .split(' ')
    .filter(Boolean)
    .map(value => value[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

export function UserAvatar({
  user,
  className = '',
}: {
  user: User;
  className?: string;
}) {
  const [failed, setFailed] = useState(false);
  const source = useMemo(() => api.avatarUrl(user), [user.has_avatar, user.avatar_updated_at]);

  useEffect(() => setFailed(false), [source]);

  return <span className={`user-avatar ${className}`.trim()} aria-label={`${user.full_name} profile image`}>
    {source && !failed
      ? <img src={source} alt="" onError={() => setFailed(true)}/>
      : <span className="user-avatar-fallback">{initials(user.full_name)}</span>}
  </span>;
}
