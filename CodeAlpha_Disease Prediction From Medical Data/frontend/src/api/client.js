const API_BASE = import.meta.env.VITE_API_BASE || '/api'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })

  if (response.status === 204) return null
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = response.status === 401 ? 'Your session has expired. Please sign in again.' : (typeof payload.detail === 'string' ? payload.detail : 'Something went wrong. Please try again.')
    const error = new Error(detail)
    error.status = response.status
    throw error
  }
  return payload
}

export const api = {
  login: (body) => request('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  register: (body) => request('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  me: () => request('/auth/me'),
  updateProfile: (body) => request('/auth/profile', { method: 'POST', body: JSON.stringify(body) }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  health: () => request('/health'),
  predict: (body) => request('/prediction/heart', { method: 'POST', body: JSON.stringify(body) }),
  modelReport: () => request('/models/report'),
  datasetReport: () => request('/models/dataset'),
}
