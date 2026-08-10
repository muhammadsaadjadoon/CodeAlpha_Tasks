const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

export async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: options.body instanceof FormData ? undefined : { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const contentType = res.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await res.json() : await res.text();
  if (!res.ok) {
    const message = typeof data === 'string' ? data : data.detail || 'Request failed. Please try again.';
    throw new Error(message);
  }
  return data;
}

export function downloadUrl(path) {
  return `${API_BASE}${path}`;
}
