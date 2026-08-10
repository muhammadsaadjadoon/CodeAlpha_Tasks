import type { Theme } from '../types';

export function Brand({
  theme,
  compact = false,
  className = '',
}: {
  theme: Theme;
  compact?: boolean;
  className?: string;
}) {
  const effective =
    theme === 'system'
      ? matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      : theme;

  return (
    <div className={`wl-brand ${compact ? 'compact' : ''} ${className}`.trim()}>
      <span className="wl-brand-mark">
        <img
          src={effective === 'dark' ? '/brand/writelens-dark.png' : '/brand/writelens-light.png'}
          alt="WriteLens"
        />
      </span>
      <span className="wl-brand-copy">
        <strong>WriteLens</strong>
        <small>See What You Write</small>
      </span>
    </div>
  );
}
