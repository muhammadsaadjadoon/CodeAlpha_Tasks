import type { AnalysisHistoryPage, AnalysisResult, ModelStatus, Theme, User } from './types';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    credentials: 'include',
    cache: 'no-store',
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    let message = 'The request could not be completed.';
    try {
      const payload = await response.json();
      message = payload.detail || payload.error || message;
    } catch {}
    throw new Error(message);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export const api = {
  me: () => request<User>('/api/auth/me'),
  login: (email: string, password: string) => request<User>('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (full_name: string, email: string, password: string) => request<User>('/api/auth/register', { method: 'POST', body: JSON.stringify({ full_name, email, password }) }),
  logout: () => request<void>('/api/auth/logout', { method: 'POST' }),
  updateProfile: (full_name: string) => request<User>('/api/profile', { method: 'PATCH', body: JSON.stringify({ full_name }) }),
  updateTheme: (theme: Theme) => request<User>('/api/profile/theme', { method: 'PATCH', body: JSON.stringify({ theme }) }),
  uploadAvatar: (file: File) => {
    const data = new FormData();
    data.append('avatar', file, file.name);
    return request<User>('/api/profile/avatar', { method: 'PUT', body: data });
  },
  deleteAvatar: () => request<User>('/api/profile/avatar', { method: 'DELETE' }),
  avatarUrl: (user: User) => user.has_avatar
    ? `/api/profile/avatar?v=${encodeURIComponent(user.avatar_updated_at || 'current')}`
    : '',
  analyze: (file: File | Blob, filename = 'recording.wav', sourceType: 'recording' | 'upload' = 'upload') => {
    const data = new FormData();
    data.append('audio', file, filename);
    data.append('source_type', sourceType);
    return request<AnalysisResult>('/api/analysis/voice', { method: 'POST', body: data });
  },
  history: (limit = 50, offset = 0) => request<AnalysisHistoryPage>(`/api/analysis/history?limit=${limit}&offset=${offset}`),
  deleteHistory: (id: number) => request<void>(`/api/analysis/history/${id}`, { method: 'DELETE' }),
  clearHistory: () => request<void>('/api/analysis/history', { method: 'DELETE' }),
  modelStatus: () => request<ModelStatus>('/api/analysis/model-status'),
};
