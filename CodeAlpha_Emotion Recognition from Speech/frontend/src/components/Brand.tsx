import type { Theme } from '../types';

export function Brand({ theme, compact = false }: { theme: Theme; compact?: boolean }) {
  const effective = theme === 'system'
    ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : theme;

  const fullLogo = effective === 'dark'
    ? '/brand/inflect-dark.png'
    : '/brand/inflect-light.png';

  const markLogo = effective === 'dark'
    ? '/brand/inflect-mark-dark.png'
    : '/brand/inflect-mark-light.png';

  return <div
    className={`brand brand-image-lockup brand-${effective} ${compact ? 'compact' : ''}`}
    aria-label="INFLECT"
  >
    <img className="brand-full-logo" src={fullLogo} alt="INFLECT"/>
    <img className="brand-mark-logo" src={markLogo} alt="" aria-hidden="true"/>
  </div>;
}
